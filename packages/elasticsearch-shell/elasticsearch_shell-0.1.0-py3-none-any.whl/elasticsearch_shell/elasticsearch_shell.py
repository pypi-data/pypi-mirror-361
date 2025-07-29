#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "elasticsearch==8.17.1",
#   "prompt-toolkit",
# ]
# [tool.uv]
# exclude-newer = "2025-07-01T00:00:00Z"
# ///
from elasticsearch import Elasticsearch
import os
import json
import time
import argparse
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import Completer, Completion


class ESCompleter(Completer):
    def __init__(self, es_client):
        self.client = es_client
        self.methods = ["GET", "POST", "PUT", "DELETE", "HEAD"]
        self.common_paths = [
            "_search",
            "_count",
            "_mapping",
            "_cat/indices",
            "_cat/nodes",
            "_aliases",
        ]
        self.query_dsl_keywords = sorted(
            [
                # Top level
                "query",
                "aggs",
                "size",
                "from",
                "sort",
                "_source",
                "script_fields",
                "stored_fields",
                "docvalue_fields",
                "highlight",
                "rescore",
                "explain",
                "version",
                "indices_boost",
                "min_score",
                "search_after",
                "pit",
                # Query types
                "match",
                "match_all",
                "match_phrase",
                "match_phrase_prefix",
                "multi_match",
                "common",
                "query_string",
                "simple_query_string",
                "term",
                "terms",
                "terms_set",
                "range",
                "exists",
                "prefix",
                "wildcard",
                "regexp",
                "fuzzy",
                "type",
                "ids",
                "bool",
                "boosting",
                "constant_score",
                "dis_max",
                "function_score",
                "script",
                "script_score",
                # Bool query clauses
                "must",
                "filter",
                "should",
                "must_not",
                # Aggregations
                "avg",
                "cardinality",
                "extended_stats",
                "geo_bounds",
                "geo_centroid",
                "max",
                "min",
                "percentiles",
                "percentile_ranks",
                "stats",
                "sum",
                "value_count",
                "terms",
                "significant_terms",
                "range",
                "date_range",
                "ip_range",
                "histogram",
                "date_histogram",
                "geo_distance",
                "filter",
                "filters",
                "global",
                "missing",
                "nested",
                "reverse_nested",
                "sampler",
                "top_hits",
                # Other
                "boost",
                "slop",
                "fuzziness",
                "operator",
                "zero_terms_query",
                "cutoff_frequency",
                "auto_generate_synonyms_phrase_query",
                "analyzer",
                "fields",
                "type",
                "tie_breaker",
                "minimum_should_match",
                "lenient",
                "rewrite",
                "value",
                "relation",
                "time_zone",
                "format",
                "gte",
                "gt",
                "lte",
                "lt",
            ]
        )
        self._cache = []
        self._cache_time = 0
        self.cache_ttl_seconds = 60

    def get_indices_and_aliases(self):
        now = time.time()
        if now - self._cache_time > self.cache_ttl_seconds:
            try:
                indices = self.client.cat.indices(h="index", format="json")
                aliases = self.client.cat.aliases(h="alias", format="json")
                self._cache = sorted(
                    list(
                        set(
                            [i["index"] for i in indices]
                            + [a["alias"] for a in aliases]
                        )
                    )
                )
                self._cache_time = now
            except Exception:
                # In case of error, return old cache and try again next time
                return self._cache or []
        return self._cache

    def get_completions(self, document, complete_event):
        text = document.text

        # If we are in the body (multi-line input)
        if "\n" in text:
            # Logic for JSON body completion
            word_before_cursor = document.get_word_before_cursor()

            to_replace = word_before_cursor
            last_delim_pos = -1
            for char in ["{", "[", ","]:
                last_delim_pos = max(last_delim_pos, word_before_cursor.rfind(char))

            if last_delim_pos != -1:
                to_replace = word_before_cursor[last_delim_pos + 1 :]

            clean_word = to_replace.lstrip('"')

            for keyword in self.query_dsl_keywords:
                if keyword.startswith(clean_word):
                    completion = f'"{keyword}"'
                    yield Completion(completion, start_position=-len(to_replace))
            return

        # If we are on the first line (request line)
        word_before_cursor = document.get_word_before_cursor(WORD=True)
        words = document.text.split()

        # If we are completing the first word.
        if len(words) == 0 or (len(words) == 1 and not document.text.endswith(" ")):
            # Complete method
            for method in self.methods:
                if method.startswith(word_before_cursor.upper()):
                    yield Completion(method, start_position=-len(word_before_cursor))
        # If we are completing the path
        elif len(words) >= 1 and words[0].upper() in self.methods:
            # Complete path
            all_paths = self.get_indices_and_aliases() + self.common_paths
            for path in all_paths:
                if path.startswith(word_before_cursor):
                    yield Completion(path, start_position=-len(word_before_cursor))


def get_history_file_path():
    """Get the path to the history file according to XDG Base Directory Spec."""
    xdg_state_home = os.getenv("XDG_STATE_HOME", os.path.expanduser("~/.local/state"))
    app_state_dir = os.path.join(xdg_state_home, "elasticsearch-shell")
    os.makedirs(app_state_dir, exist_ok=True)
    return os.path.join(app_state_dir, "history")


def main():
    parser = argparse.ArgumentParser(
        description="A REPL for Elasticsearch.",
        epilog="""Connection details are configured via environment variables.
Two connection methods are supported:

1. Cloud ID and API Key:
   ES_CLOUD_ID: Your cloud ID
   ES_API_KEY: Your API key in 'id:key' format

2. Host, Username, and Password:
   ES_HOST: The host and port of your Elasticsearch instance (e.g., https://localhost:9200)
   ES_USERNAME: The username for basic authentication
   ES_PASSWORD: The password for basic authentication
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.parse_args()

    es_cloud_id = os.getenv("ES_CLOUD_ID")
    es_api_key = os.getenv("ES_API_KEY")
    es_host = os.getenv("ES_HOST")

    client = None
    if es_cloud_id and es_api_key:
        try:
            key_id, api_key_secret = es_api_key.split(":", 1)
            client = Elasticsearch(cloud_id=es_cloud_id, api_key=(key_id, api_key_secret))
        except ValueError:
            print("Error: ES_API_KEY must be in 'id:key' format.")
            return
    elif es_host:
        es_username = os.getenv("ES_USERNAME")
        es_password = os.getenv("ES_PASSWORD")
        client = Elasticsearch([es_host], basic_auth=(es_username, es_password))
    else:
        print("Error: No connection configuration found.")
        parser.print_help()
        return

    if not client.ping():
        print("Could not connect to Elasticsearch. Exiting.")
        return

    history = FileHistory(get_history_file_path())
    completer = ESCompleter(client)
    session = PromptSession(history=history, completer=completer)

    print(
        "Connected to Elasticsearch. Enter a request and press Meta+Enter (or Esc then Enter) to submit. Ctrl+D to exit."
    )

    while True:
        try:
            full_request = session.prompt(">>> ", multiline=True)

            if not full_request.strip():
                continue

            request_lines = full_request.split("\n")
            request_line = request_lines[0]
            body_lines = request_lines[1:]

            parts = request_line.split()
            if len(parts) < 2:
                print("Invalid command. Use 'METHOD /path'.")
                continue

            method = parts[0].upper()
            path = parts[1]
            if not path.startswith("/"):
                path = "/" + path

            body = None
            if body_lines:
                body_str = "\n".join(body_lines)
                try:
                    body = json.loads(body_str)
                except json.JSONDecodeError as e:
                    print(f"Invalid JSON body: {e}")
                    continue

            try:
                headers = None
                if body is not None:
                    headers = {
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    }
                response = client.perform_request(
                    method, path, body=body, headers=headers
                )
                print(json.dumps(response.body, indent=2))
            except Exception as e:
                print(f"Error: {e}")

        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break


if __name__ == "__main__":
    main()
