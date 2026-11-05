#!/bin/sh
set -eu
project_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
package_dir="$project_root/vendor/rednote-runtime/node_modules/rednote-mind-mcp"
patch_file="$project_root/patches/rednote-mind-mcp-0.3.0.patch"
node_binary="$project_root/vendor/node-runtime/bin/node"
version=$("$node_binary" -p "require(process.argv[1]).version" "$package_dir/package.json")
if [ "$version" != "0.3.0" ]; then
  echo "Expected rednote-mind-mcp 0.3.0; found $version. Refusing to patch." >&2
  exit 1
fi
if patch -f --dry-run --silent -R -p1 -d "$package_dir" < "$patch_file" >/dev/null 2>&1; then
  echo "rednote compatibility patch already applied"
elif patch -f --dry-run --silent -p1 -d "$package_dir" < "$patch_file"; then
  patch -f -p1 -d "$package_dir" < "$patch_file"
else
  echo "Package differs from both supported states; inspect before changing it." >&2
  exit 1
fi
