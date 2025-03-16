const fs = require("fs");
const path = require("path");
const CopyPlugin = require("copy-webpack-plugin");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const ESLintPlugin = require("eslint-webpack-plugin");
const StylelintPlugin = require("stylelint-webpack-plugin");

const projectRoot = "milk2meat";

const options = {
  entry: {
    // multiple entries can be added here
    main: `./${projectRoot}/assets/js/main.js`,
    editor: `./${projectRoot}/assets/js/editor.js`,
    "pdf-viewer": `./${projectRoot}/assets/js/pdf-viewer.js`,
    "pdf.worker": path.resolve(
      __dirname,
      "node_modules/pdfjs-dist/build/pdf.worker.mjs",
    ),
    "esv-integration": `./${projectRoot}/assets/js/esv-integration.js`,
  },
  output: {
    path: path.resolve(`./${projectRoot}/static/`),
    // based on entry name, e.g. main.js
    filename: "js/[name].min.js", // based on entry name, e.g. main.js
    clean: true,
  },
  plugins: [
    new CopyPlugin({
      patterns: [
        {
          // Copy images to be referenced directly by Django to the "img" subfolder in static files.
          from: "img",
          context: path.resolve(`./${projectRoot}/assets/`),
          to: path.resolve(`./${projectRoot}/static/img`),
        },
        {
          // Copy favicons to be referenced directly by Django to the "ico" subfolder in static files.
          from: "ico",
          context: path.resolve(`./${projectRoot}/assets/`),
          to: path.resolve(`./${projectRoot}/static/ico`),
        },
      ],
    }),
    new MiniCssExtractPlugin({
      filename: "css/[name].min.css",
    }),
    new ESLintPlugin({
      failOnError: false,
      lintDirtyModulesOnly: true,
      emitWarning: true,
    }),
    new StylelintPlugin({
      failOnError: false,
      lintDirtyModulesOnly: true,
      emitWarning: true,
      extensions: ["css"],
    }),
  ],
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: "babel-loader",
        },
      },
      {
        // this will apply to `.sass` / `.scss` / `.css` files
        test: /\.(s[ac]ss|css)$/,
        use: [
          MiniCssExtractPlugin.loader,
          {
            loader: "css-loader",
            options: {
              sourceMap: true,
            },
          },
          {
            loader: "postcss-loader",
            options: {
              sourceMap: true,
            },
          },
        ],
      },
      {
        // sync font files referenced by the css to the fonts directory
        // the publicPath matches the path from the compiled css to the font file
        test: /\.(woff|woff2)$/,
        include: /fonts/,
        type: "asset/resource",
        generator: {
          filename: "fonts/[name][ext]",
        },
      },
      {
        // Handle images referenced in CSS files (like in EasyMDE)
        test: /\.(png|jpe?g|gif|svg)$/i,
        type: "asset/resource",
        generator: {
          filename: "img/[name][ext]",
        },
      },
    ],
  },
  // externals are loaded via base.html and not included in the webpack bundle.
  externals: {
    // gettext: 'gettext',
  },
  // https://github.com/highcharts/highcharts/issues/20929#issuecomment-2036318755
  resolve: {
    modules: [".", "node_modules"],
  },
};

/*
  If a project requires internationalisation, then include `gettext` in base.html
    via the Django JSi18n helper, and uncomment it from the 'externals' object above.
*/

const webpackConfig = (environment, argv) => {
  const isProduction = argv.mode === "production";

  options.mode = isProduction ? "production" : "development";

  if (!isProduction) {
    // https://webpack.js.org/configuration/stats/
    const stats = {
      // Tells stats whether to add the build date and the build time information.
      builtAt: false,
      // Add chunk information (setting this to `false` allows for a less verbose output)
      chunks: false,
      // Add the hash of the compilation
      hash: false,
      // `webpack --colors` equivalent
      colors: true,
      // Add information about the reasons why modules are included
      reasons: false,
      // Add webpack version information
      version: false,
      // Add built modules information
      modules: false,
      // Show performance hint when file size exceeds `performance.maxAssetSize`
      performance: false,
      // Add children information
      children: false,
      // Add asset Information.
      assets: false,
    };

    options.stats = stats;

    // Create JS source maps in the dev mode
    // See https://webpack.js.org/configuration/devtool/ for more options
    options.devtool = "inline-source-map";

    // See https://webpack.js.org/configuration/dev-server/.
    options.devServer = {
      // Enable gzip compression for everything served.
      compress: true,
      watchFiles: [`./${projectRoot}/**/*.html`],
      // hot: true,
      hot: false,
      client: {
        logging: "error",
        // Shows a full-screen overlay in the browser when there are compiler errors.
        overlay: true,
      },
      static: false,
      host: "0.0.0.0",
      allowedHosts: ["all"],
      port: 3000,
      devMiddleware: {
        index: false, // specify to enable root proxying
        publicPath: "/static/",
        // Write compiled files to disk. This makes live-reload work on both port 3000 and 8000.
        writeToDisk: true,
      },
      proxy: [
        {
          context: () => true,
          target: "http://127.0.0.1:8000",
        },
      ],
    };
  }

  return options;
};

module.exports = webpackConfig;
