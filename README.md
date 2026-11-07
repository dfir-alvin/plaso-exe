# plaso-windows-build

Unofficial portable Windows builds of [plaso (log2timeline)](https://github.com/log2timeline/plaso). This repo has NO association with the developers of log2timeline or plaso; it is recommended you use the docker route or SANS SIFT instead when possible. Releases are considered experimental and unsupported. 

GitHub Actions workflow checks plaso's latest release. If this repo has no
release with that tag yet, it:

1. checks out plaso at that tag on a `windows-2025` runner,
2. installs it with Python 3.13 (every native dependency ships a `win_amd64` wheel on PyPI),
3. freezes all five tools with PyInstaller into **one onedir folder** sharing a single `_internal\`,
4. smoke-tests the frozen exes (extracts `test_data\vsstest.qcow2`, runs `pinfo` and `psort`, checks the event count),
5. publishes `plaso-<tag>-py3.13-amd64.zip` and a `.sha256` file as a release here, under the same tag.

## Layout

```
.github/workflows/build.yml   check -> build (Windows) -> release
plaso.spec                     PyInstaller spec: 5 EXEs, one COLLECT
```

## Manual runs

Actions → **plaso-windows** → *Run workflow*. You can give a specific upstream tag
(for example `20260720`) and tick **force** to rebuild and replace an existing release.

## Usage

Unzip anywhere and run the tools from that folder:

```
log2timeline.exe --storage-file case.plaso E:\image.E01
psort.exe -o dynamic -w timeline.csv case.plaso
```

## Notes

- Python 3.14 isn't used yet because `yara-python` and `zstd` don't publish Windows wheels for it.
- UPX is turned off. Packed `.pyd` files make antivirus false positives worse. PyInstaller
  bootloaders still get flagged now and then, so publish the hashes and consider code-signing.
- The repo stays active through its releases. Scheduled workflows on public repos are disabled
  after 60 days without activity, and plaso only releases a few times a year, so you may have
  to re-enable the schedule (or add a keepalive) after quiet periods.
