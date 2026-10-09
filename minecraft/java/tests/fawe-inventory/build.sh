#!/bin/sh
set -eu
# Usage: build.sh /absolute/isolated-paper-directory /absolute/output.jar
server=${1:?isolated Paper directory required}
output=${2:?output JAR path required}
source_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
build=$(mktemp -d)
trap 'rm -rf -- "$build"' EXIT
classpath=$(find "$server/libraries" "$server/versions" "$server/plugins" -name '*.jar' -type f -print | paste -sd ':' -)
javac --release 25 -cp "$classpath" -d "$build" "$source_dir/FaweInventoryProbe.java"
cp "$source_dir/plugin.yml" "$build/plugin.yml"
jar --create --file "$output" -C "$build" .
