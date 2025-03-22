# Changelog

All notable changes to this project will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project attempts to adhere to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v1.1.0](https://github.com/engineervix/milk2meat/compare/v1.0.0...v1.1.0) (2025-03-22)


### 🚀 Features

* add ajax endpoints for Note create/update ([18461df](https://github.com/engineervix/milk2meat/commit/18461dfbe880c5881051735c153884290fbc5b65))
* ajax-based book updates ([8545d61](https://github.com/engineervix/milk2meat/commit/8545d616a3154620b775efff5b316b99fe06231e))
* allow for deletion of files from Notes ([d00260e](https://github.com/engineervix/milk2meat/commit/d00260e9b38d9607f2979d7ca8ebb49599984134))
* editor save enhancements ([05e18b6](https://github.com/engineervix/milk2meat/commit/05e18b6ff8d5bb277a0eb0f87691fb9fc44ec52a))
* frontend updates for AJAX-based Note submissions ([f4016c0](https://github.com/engineervix/milk2meat/commit/f4016c06030686426c3df4a68bb7e15fc14451a2))


### 🐛 Bug Fixes

* prevent unsaved changes warning when submitting forms ([c0a9124](https://github.com/engineervix/milk2meat/commit/c0a912478627398cb1f6f1b1d837704238aaecd2))


### ♻️ Code Refactoring

* cleanup after AJAX-based changes from 18461df to 8545d61 ([c072d0c](https://github.com/engineervix/milk2meat/commit/c072d0c2f84910b71449a254a8f7b3a4ac73e1a4))
* fix beforeunload event handling for Ajax submissions ([35d48af](https://github.com/engineervix/milk2meat/commit/35d48afe2cc250d8e23b17dee9122fec4461d294))
* improve notifications with centered toast & use Phosphor icons ([e42fddb](https://github.com/engineervix/milk2meat/commit/e42fddb20faeba10a966b7d340f413c55c715691))
* **js:** isolate template JS into dedicated modules ([83f5033](https://github.com/engineervix/milk2meat/commit/83f50336331728b736ced2a05cbd1f527c34fd6c))
* **js:** modularize note form JavaScript code ([34ee9eb](https://github.com/engineervix/milk2meat/commit/34ee9eb2be3c83ec15fd6c37c4db0edc909af322))
* replace BLB ScriptTagger with ESV Cross-Reference Tool ([ef9c4b1](https://github.com/engineervix/milk2meat/commit/ef9c4b195e62ee8ebba48a391f74d2cd572d69df))
* we don't need django admin ([bb35262](https://github.com/engineervix/milk2meat/commit/bb352627af21870b729cbe1de46181ce638347c6))


### ⚙️ Build System

* **deps:** update dependency boto3 to v1.37.13 ([2b02fdd](https://github.com/engineervix/milk2meat/commit/2b02fdd3a6e9b7b1921168ce4b2ced8985979153))
* **deps:** update dependency django to v5.1.7 ([ec17e5e](https://github.com/engineervix/milk2meat/commit/ec17e5eee6d2f696194fe788003b4d9a9342f133))
* **deps:** update dependency django-environ to v0.12.0 ([#9](https://github.com/engineervix/milk2meat/issues/9)) ([40949b9](https://github.com/engineervix/milk2meat/commit/40949b932106d079b2e46e63c096a1efbd19335d))
* **deps:** update dependency mkdocs-git-revision-date-localized-plugin to v1.4.5 ([#5](https://github.com/engineervix/milk2meat/issues/5)) ([7bbdd48](https://github.com/engineervix/milk2meat/commit/7bbdd48c53be1df32d8a7fde17d0713d1702df26))
* **deps:** update dependency mkdocs-material to v9.6.8 ([#6](https://github.com/engineervix/milk2meat/issues/6)) ([c557ce5](https://github.com/engineervix/milk2meat/commit/c557ce5f26da72ad9338402d131a928d8cde7918))
* **deps:** update dependency ruff to ^0.11.0 ([#10](https://github.com/engineervix/milk2meat/issues/10)) ([d2f03bf](https://github.com/engineervix/milk2meat/commit/d2f03bf202704f8cd8830a2266575ae8b57f410a))

## 1.0.0 (2025-03-12)


### 🚀 Features

* add Book intros ([975fcdc](https://github.com/engineervix/milk2meat/commit/975fcdcc1a7b30c8f8c6eec2026ba8c6ed265d35))
* add custom storage backend for private media files ([2957497](https://github.com/engineervix/milk2meat/commit/2957497120a0c96a6912635274aaaf3e9a268e6e))
* add management command for generating fake data for testing ([94e8ef2](https://github.com/engineervix/milk2meat/commit/94e8ef245fd672ff6ebb09b22e0dc620335cc7b1))
* add navbar & footer ([c660b36](https://github.com/engineervix/milk2meat/commit/c660b368c3611bf39f76cabac9f2faf03f816b0f))
* filesize/type information ([9bd2a3d](https://github.com/engineervix/milk2meat/commit/9bd2a3d4c90022b5f40b90c1b4f72e2ffa81d888))
* glightbox ([8adb2f1](https://github.com/engineervix/milk2meat/commit/8adb2f16c5a86c0149ce01294f13ed20a32db3ae))
* global search ([ab298c3](https://github.com/engineervix/milk2meat/commit/ab298c37200f219a069ded92d2ae928a9ec9acde))
* handle multi-page pdfs ([4f58bbf](https://github.com/engineervix/milk2meat/commit/4f58bbf3f10ab50ec2f46a22dace6868b4e76882))
* implement auth and initial starter templates ([9d0967b](https://github.com/engineervix/milk2meat/commit/9d0967b71d6a4dd1f879212012ced25701f5b518))
* management command to add books of the Bible ([687311d](https://github.com/engineervix/milk2meat/commit/687311d7d75da0c406953b44cf7a0ca10f92fe25))
* notes - initial implementation (not complete) ([ce39fda](https://github.com/engineervix/milk2meat/commit/ce39fda351253e4487c2fca42c1266d827a07d13))
* paste rich text to md ([44f02c1](https://github.com/engineervix/milk2meat/commit/44f02c1b38370ab45acf6a4ca4e834771f9599c3))
* render md ([315d91a](https://github.com/engineervix/milk2meat/commit/315d91a4ef4ce028c8b9f2a174b5f7e2f825c38c))
* search notes ([a859a11](https://github.com/engineervix/milk2meat/commit/a859a118bcfc4029b0c402884519e024d9a9e336))
* simpler home page ([eabc22b](https://github.com/engineervix/milk2meat/commit/eabc22b436a81ccae8a545afc3fe7ece1dd3558c))
* split a string on the given separator and return a list of parts ([95912a7](https://github.com/engineervix/milk2meat/commit/95912a72aaa9e1ab7d8755dc70dc38c1cf4e1493))
* starting point for a new django project ([2d92f1a](https://github.com/engineervix/milk2meat/commit/2d92f1a411e442873b435509c974eb97fb0cfe50))
* use beforeunload to warn about unsaved changes ([ff7ea71](https://github.com/engineervix/milk2meat/commit/ff7ea71c38b46fb679c29fba2b7ca1813f8ab224))


### 🐛 Bug Fixes

* a couple of bugfixes relating to creating/updating notes ([667b22b](https://github.com/engineervix/milk2meat/commit/667b22b2435c4b13de36449d7c0dd215f9f34e14))
* correct numbering of search results ([9a876c0](https://github.com/engineervix/milk2meat/commit/9a876c0216859ff4b438e49f5e9adc59d99ab969))
* dark mode and switcher ([1823249](https://github.com/engineervix/milk2meat/commit/1823249692f747b31d6bdaaa67ed5ceb2c36377a))
* dark mode for easyMDE, also remove transition effects ([ea23710](https://github.com/engineervix/milk2meat/commit/ea2371071635d5c519ba4cbab482094965fd799f))
* dark/light toggle ([a153e95](https://github.com/engineervix/milk2meat/commit/a153e95662f51578e6db1db2533117103d7f1638))
* easyMDE initialisation ([4eae346](https://github.com/engineervix/milk2meat/commit/4eae346491d3496e84dbc85b2694dafac99eaffb))
* ensure cursor is visible in dark mode on easyMDE editor ([aa5d734](https://github.com/engineervix/milk2meat/commit/aa5d73490950ad69e8d4d5f28c2118ff3def672b))
* ensure PrivateS3Storage loads settings at instance creation ([cade30f](https://github.com/engineervix/milk2meat/commit/cade30fd2c25b5539b5885b5e470c4592659e130))
* exception handling ([ae30a45](https://github.com/engineervix/milk2meat/commit/ae30a4588ff74e1b9a4c7a4a0fd0a54811bbece9))
* max chars ([3749b9a](https://github.com/engineervix/milk2meat/commit/3749b9a092136a94b971db56356f9658b6a3bf5e))
* pdf viewer in development environment ([b01c974](https://github.com/engineervix/milk2meat/commit/b01c974d15e8c47478024819f376aefe588a130d))
* taggit and uuids ([9fd56a4](https://github.com/engineervix/milk2meat/commit/9fd56a43b389bdcb7f51e597a1f391f2ef978f36))
* tags on note list view ([7264976](https://github.com/engineervix/milk2meat/commit/7264976c7b4bde7558f9d065a04dcfe277812e24))
* template syntax ([abb8490](https://github.com/engineervix/milk2meat/commit/abb8490b80cf64d7f11cc87512df2d1848bc609c))
* timeline rendering ([5cee3ab](https://github.com/engineervix/milk2meat/commit/5cee3ab0464c028d09932a0f2a5eea21a5fc2e4a))
* warn when exiting with unsaved changes ([be151ea](https://github.com/engineervix/milk2meat/commit/be151ea2dd3c5d2665788158a5c3e0ff98dd8224))


### 📝 Docs

* add screenshot ([30df7b6](https://github.com/engineervix/milk2meat/commit/30df7b6555fb7276d055b277041940bd526ec965))
* update README ([62b3e4b](https://github.com/engineervix/milk2meat/commit/62b3e4bdda91c1ff43d38fdd26ac26899e64f8c5))
* update README ([41b4c5d](https://github.com/engineervix/milk2meat/commit/41b4c5df3e5ec88fbf076240a637b22d46b1201c))


### 💄 Styling

* choose a more complimentary theme combo ([4da3902](https://github.com/engineervix/milk2meat/commit/4da39022d549f75b096a98e5cb498f902e9a760f))
* colour theme and dark mode ([2ccfefc](https://github.com/engineervix/milk2meat/commit/2ccfefc6fc8fb8146efca001af02a1147911969f))
* impreove login screen ([c2d1e8b](https://github.com/engineervix/milk2meat/commit/c2d1e8bb92c315798bff13fa4d0e08a656a88502))
* more fixes ([625208c](https://github.com/engineervix/milk2meat/commit/625208c27a34c90543e36238aaf3732c0438d811))
* run djlint ([4e947dc](https://github.com/engineervix/milk2meat/commit/4e947dc2261e0376d30cc983499de82091a80726))


### ♻️ Code Refactoring

* card improvements ([a22541b](https://github.com/engineervix/milk2meat/commit/a22541b38f8d8f5f636cd258f13a354b3f8d847e))
* change AWS_S3_ADDRESSING_STYLE from virtual to path ([062212a](https://github.com/engineervix/milk2meat/commit/062212aeb72d0d0d5a643d039e906f57a2f971db))
* dashboard ([285b230](https://github.com/engineervix/milk2meat/commit/285b230e4708d53ec1f6c1a734f753fa0defb877))
* handle secure file access ([d1bb52e](https://github.com/engineervix/milk2meat/commit/d1bb52ee786a0aabb58e7e56faca00fa73358b07))
* improve implementation of private storage ([f4eec52](https://github.com/engineervix/milk2meat/commit/f4eec5201c649476d9b43bfc0fd133d84d9b79d8))
* just use DaisyUI ([365e438](https://github.com/engineervix/milk2meat/commit/365e438f2bcd88ba68c06e1fb6843e23e5913ea2))
* pdf handling improvements ([7b5a342](https://github.com/engineervix/milk2meat/commit/7b5a342a757884ebd2828c07a47a09a12dda8562))
* production settings ([f3ed033](https://github.com/engineervix/milk2meat/commit/f3ed033b6e232501c7918b1cd9c3d8721104cd6f))
* production settings tweak ([7a69c94](https://github.com/engineervix/milk2meat/commit/7a69c94d65f82729ba31e677b17f56755d8c22c5))
* some colour fixes ([12ed50c](https://github.com/engineervix/milk2meat/commit/12ed50c48e9ca04792b7acbdb718ee5054fa77fb))
* split views into separate modules for better organisation ([7f6f678](https://github.com/engineervix/milk2meat/commit/7f6f678e3abb624edd954c91d8c91b28738c3e24))
* update ([a903187](https://github.com/engineervix/milk2meat/commit/a90318749f9374cd562a9d89db7c5335caf50b43))
* use models.UniqueConstraints instead of unique_together ([88d8375](https://github.com/engineervix/milk2meat/commit/88d8375025fe75c424e2036ca91bea951f21f3aa))
* use reverse instead of reverse_lazy ([3bcd8eb](https://github.com/engineervix/milk2meat/commit/3bcd8ebadcd97a6f4c48e0896db2336b5631588d))


### ✅ Tests

* add some tests ([9b9468d](https://github.com/engineervix/milk2meat/commit/9b9468d824190e3e98e6092d883718b6ed6dea03))
* add tests for custom storage backend, and reorganize tests ([ce18264](https://github.com/engineervix/milk2meat/commit/ce182646da00e3eef0d95887954868a669f15a64))
* add tests for management commands ([070f20f](https://github.com/engineervix/milk2meat/commit/070f20f9db93add5ff74bfa68324593f4d15ad80))
* add turnstile tests ([80c105f](https://github.com/engineervix/milk2meat/commit/80c105f2e6d1b8b4f9529d68e87ba4be7a868e4a))
* minor fixes ([9de05d3](https://github.com/engineervix/milk2meat/commit/9de05d380279f10f46cd6f2611cb1c317c6127c8))
* test the models ([778f7e6](https://github.com/engineervix/milk2meat/commit/778f7e6cb30f3cd08a8f08f5f29b781cd1098569))


### ⚙️ Build System

* add django as extra to sentry ([a9b2a36](https://github.com/engineervix/milk2meat/commit/a9b2a36ef4727a926169a6ec064fcdb907bbbf61))
* add Dockerfile for productio deployment ([c560cb4](https://github.com/engineervix/milk2meat/commit/c560cb4b6d5ce1f078501052e846e5eeff5fdb7f))
* add dokku deploy script ([ef248b4](https://github.com/engineervix/milk2meat/commit/ef248b49660b2345a107d1f77419cc06720fbe3a))
* add requests ([dfd0e32](https://github.com/engineervix/milk2meat/commit/dfd0e3205d59f7ca8b60f66373eca3c5d2f6ea94))
* add the packages we may need to use later on ([f581995](https://github.com/engineervix/milk2meat/commit/f5819957d5c3313b5a151786d8ba3bfeac7fc73b))
* deployment setup ([4ec50ff](https://github.com/engineervix/milk2meat/commit/4ec50ffdaf154a036ac38f72610062f5f9b40a29))
* remove unused dependencies ([026403f](https://github.com/engineervix/milk2meat/commit/026403f9dabeda4a5d856d3b1a58ce1c523025e0))


### 👷 CI/CD

* add coverage badge ([e0a035b](https://github.com/engineervix/milk2meat/commit/e0a035b7bc4da0e8e08c1a3b792c7773684040e3))
* bump actions/upload-artifact to v4 ([812bf40](https://github.com/engineervix/milk2meat/commit/812bf40e8368f8aa3c152c10ce6b6e4fd3214e79))
* fix reference to python_tests ([caf1a95](https://github.com/engineervix/milk2meat/commit/caf1a95451bb007a863b37caf0aa7b0b14267954))
* github actions and renovate setup ([4abb5e2](https://github.com/engineervix/milk2meat/commit/4abb5e2b3918345ed9c7ba3d761366eb9e394b7a))
* resolve dependency installation issues in CI workflow ([bb696d9](https://github.com/engineervix/milk2meat/commit/bb696d9ce5fae367685cdfe6e438a634c7355f0e))
