# alpine-ostree apk repository

Pre-built Alpine Linux packages:

| package  | version | purpose |
|----------|---------|---------|
| `composefs` | 1.0.8 | file system for mounting container images (`libcomposefs`, `mkcomposefs`, …). This build carries `replaces=composefs` so it supersedes any official package of the same name. |
| `ostree`  | 2026.2  | OSTree, built **with composefs support** (`--with-composefs=yes`), plus the usual subpackages (`ostree-dev`, `ostree-doc`, `ostree-dbg`, `ostree-gir`, `ostree-grub`, `ostree-bash-completion`, `ostree-mkinitfs`) and `ostree-trivial-httpd`. |

Built from upstream releases on every push to `main` by
[`.github/workflows/build.yml`](.github/workflows/build.yml) for:

* Alpine **v3.24**
* architectures: **x86_64 (amd64)**, **aarch64**

The resulting apk repository is published to **GitHub Pages** (modern
`upload-pages-artifact` / `deploy-pages` workflow, not a git branch).

## Repository URLs

```
https://<user>.github.io/alpine-ostree/v3.24/main
```

(apk appends the architecture directory automatically: `.../v3.24/main/x86_64` or
`.../v3.24/main/aarch64`).

## Using it

```sh
# on an Alpine 3.24 system:
wget -O /etc/apk/keys/zhangyoufu.rsa.pub \
  https://<user>.github.io/alpine-ostree/keys/zhangyoufu.rsa.pub
echo "https://<user>.github.io/alpine-ostree/v3.24/main" >> /etc/apk/repositories
apk update
apk add ostree          # pulls composefs automatically
```

`ostree --version` should list `composefs` under Features.

## Building locally

```sh
apk add abuild
# prepare a signing key:
mkdir -p ~/.abuild
echo "PACKAGER='Youfu Zhang <zhangyoufu@gmail.com>'" > ~/.abuild/abuild.conf
openssl genrsa -out ~/.abuild/zhangyoufu.rsa 4096
echo "PACKAGER_PRIVKEY='$HOME/.abuild/zhangyoufu.rsa'" >> ~/.abuild/abuild.conf
openssl rsa -in ~/.abuild/zhangyoufu.rsa -pubout -out ~/.abuild/zhangyoufu.rsa.pub
cp ~/.abuild/*.rsa.pub /etc/apk/keys/

# build composefs first, then ostree (its makedepends pull composefs-dev):
cd main/composefs && abuild -F -r -P "$PWD/../../repo/v3.24"
abuild index
echo "file://$PWD/../../repo/v3.24" >> /etc/apk/repositories
apk update
cd ../ostree && abuild -F -r -P "$PWD/../../repo/v3.24"
```
