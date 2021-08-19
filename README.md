# doc-build github action

This action build [sphinx](https://www.sphinx-doc.org/) documentation.

## Inputs

### `docs`

**Required** The location of the documentation source to build. Default `"docs"`.

### `dest`

**Required** The destination directory. Default `"build"`.

## Example usage

```
uses: andreasofthings/doc-build@v13
with:
  docs: 'docs'
  dest: 'build'
```
