# Changelog

All notable changes to this project will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project attempts to adhere to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v2.0.0](https://github.com/engineervix/milk2meat/compare/v1.1.0...v2.0.0) (2025-03-23)


### ⚠ BREAKING CHANGES

* the `core` app was becoming unwieldy, so various
functionality has been moved to separate, dedicated apps for better
separation of concerns. In particular, book-related models/features
are now in the `bible` app, note-related models & features have been
moved to the `notes` app.

### 🚀 Features

* use Merriweather font for Note content & Book intro text ([5667670](https://github.com/engineervix/milk2meat/commit/5667670172a09f383d53a742b2859856ad1b4003))
* use serif font for Book intros and Note content ([48dab39](https://github.com/engineervix/milk2meat/commit/48dab39bcccbc401c6f9ffc28320836bd94a95b5))


### 🐛 Bug Fixes

* broken urls in templates & JS after the massive refactor ([9a2f0aa](https://github.com/engineervix/milk2meat/commit/9a2f0aad6a8aa431d84a4a0188ccf6bfcf9d8fc2))
* update list of directories to copy so that tailwind detects utility classes ([65f98b9](https://github.com/engineervix/milk2meat/commit/65f98b9efcb8b3de7bc905db423db9436b126bd2))
* update references to app names / models & URLs ([b075afe](https://github.com/engineervix/milk2meat/commit/b075afe50e5c8f316a0429b1e3c40a6f7543a33a))


### 📝 Docs

* add jest coverage badge ([b829121](https://github.com/engineervix/milk2meat/commit/b829121c20180166f65f78f4e1cf0041f428ca38))
* fix jest coverage badge ([5a2a3d0](https://github.com/engineervix/milk2meat/commit/5a2a3d07e0514d6551dda948d58c348f7f4387dc))
* update notes on tests ([e7a9bf0](https://github.com/engineervix/milk2meat/commit/e7a9bf030cbb584bbb5b5a10d3fb03e4f9932475))


### ♻️ Code Refactoring

* custom migrations to prevent data loss ([90528c8](https://github.com/engineervix/milk2meat/commit/90528c81ce521dc3f2baa1ab575f30809f12cb33))
* in conjuction with 90528c8, you need to specify `db_table` ([00fea03](https://github.com/engineervix/milk2meat/commit/00fea033b2cc68edddce599af7ac1ded3c15e736))
* move things around and introduce separate apps ([3cdca58](https://github.com/engineervix/milk2meat/commit/3cdca587da075175e259a441457598972d7e6240))
* rename milk2meat/assets/ to milk2meat/frontend/ ([08d43c9](https://github.com/engineervix/milk2meat/commit/08d43c91a19382ff8ba2c819f9c1a45fac66d0bd))
* we'll just recreate migrations & start fresh ([d8f1ed0](https://github.com/engineervix/milk2meat/commit/d8f1ed0b61f5f5316155e08562fc038b3c08bb21))


### ✅ Tests

* add more frontend tests ([98b3af1](https://github.com/engineervix/milk2meat/commit/98b3af18e3a579c27f722dcd4dd7ad90a011732a))
* add unit tests for tag filtering functionality in tag list page ([4b44cb1](https://github.com/engineervix/milk2meat/commit/4b44cb1322cf32d8c537841d5d3f7ef328c8ed93))
* **book-form:** add test coverage for index.js initialization ([e63c7bb](https://github.com/engineervix/milk2meat/commit/e63c7bbb7b1d18b245b368a713f100a2c74ade60))
* fix tests for pdf-viewer.js ([983de2f](https://github.com/engineervix/milk2meat/commit/983de2f5c23729f8168d08dd2ed4eedb756c6c6d))
* improve more frontend tests ([d5e88c5](https://github.com/engineervix/milk2meat/commit/d5e88c55e24aa5cf7b0608c6b1b1d5fb7eac4de6))
* improve test coverage for editor.js ([23f4c7d](https://github.com/engineervix/milk2meat/commit/23f4c7d309ed1ff52a30045f7422e109c1b30ce4))
* rewrite tests for main.js ([e2ee386](https://github.com/engineervix/milk2meat/commit/e2ee3860e8e6dce40d11e159b7ec96a88bb5f9dd))
* setup frontend testing with jest ([8414276](https://github.com/engineervix/milk2meat/commit/8414276666b73dae99338aec2c4b325f0bf86bd6))
* update jest coverage config ([190f37f](https://github.com/engineervix/milk2meat/commit/190f37f542bebdafb2e40a88018685a59b6b87ba))
* write more frontend tests ([0a90a23](https://github.com/engineervix/milk2meat/commit/0a90a23afc1906507c4b85045b720217c2a6db12))
* write tests for note-detail & note-list components ([4291c65](https://github.com/engineervix/milk2meat/commit/4291c659907194f46a8393ecc2e4f6a96ba12be4))
* write tests for note-form components ([3d711c0](https://github.com/engineervix/milk2meat/commit/3d711c09e98f2c9ca42f3ff80453dbdc918b8743))


### ⚙️ Build System

* **deps:** downgrade daisyui to v4 (reverts [#18](https://github.com/engineervix/milk2meat/issues/18)) ([c913545](https://github.com/engineervix/milk2meat/commit/c9135452994f79c85e148ede6f950bdaac55ae22))
* **deps:** downgrade eslint-webpack-plugin (reverts [#21](https://github.com/engineervix/milk2meat/issues/21)) ([23686df](https://github.com/engineervix/milk2meat/commit/23686dfccaed2c04baed645be42da4f83b82cf4c))
* **deps:** update dependency boto3 to v1.37.18 ([#24](https://github.com/engineervix/milk2meat/issues/24)) ([111cf95](https://github.com/engineervix/milk2meat/commit/111cf9504300f0abcf3b57ccdb54d926d6794d19))
* **deps:** update dependency django-debug-toolbar to v5.1.0 ([#28](https://github.com/engineervix/milk2meat/issues/28)) ([cdecf85](https://github.com/engineervix/milk2meat/commit/cdecf85a48823db8b3bb4f4d979d6d637d281054))
* **deps:** update dependency mkdocs-material to v9.6.9 ([#25](https://github.com/engineervix/milk2meat/issues/25)) ([806c96a](https://github.com/engineervix/milk2meat/commit/806c96a9b34f63d7881839adbb810d51f95b983f))
* **deps:** update dependency pre-commit to ~4.2.0 ([#29](https://github.com/engineervix/milk2meat/issues/29)) ([80ed7cf](https://github.com/engineervix/milk2meat/commit/80ed7cf6679556c145c0271e6fd79ed6274c2955))
* **deps:** update dependency ruff to v0.11.2 ([#26](https://github.com/engineervix/milk2meat/issues/26)) ([088bcff](https://github.com/engineervix/milk2meat/commit/088bcff926c2524893c6391098b6675ce710aed0))


### 👷 CI/CD

* [@renovate-bot](https://github.com/renovate-bot) should not do major updates across the board ([39805a2](https://github.com/engineervix/milk2meat/commit/39805a270c3b6fdb4a18ccb87d2f05a8a33ba4c6))
* add jest test job ([0d2deca](https://github.com/engineervix/milk2meat/commit/0d2decad77e6e9ff9ad9cb2435219a32066530f0))

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
