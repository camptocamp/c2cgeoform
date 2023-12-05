const path = require('path')
const MiniCssExtractPlugin = require('mini-css-extract-plugin')

module.exports = {
  mode: 'development',
  entry: {
    index: ['@babel/polyfill/noConflict', path.resolve(__dirname, 'src', 'index.js')],
    styles: path.resolve(__dirname, 'src', 'main.scss'),
  },
  output: {
    path: path.resolve(__dirname, 'dist'),
    libraryTarget: 'var',
    library: 'c2cgeoform',
  },
  plugins: [new MiniCssExtractPlugin()],
  devtool: 'source-map',
  module: {
    rules: [
      {
        test: /\.m?js$/,
        exclude: /(node_modules|bower_components)/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env', {}],
          },
        },
      },
      {
        test: /\.scss$/,
        use: [
          {
            loader: 'style-loader',
          },
          MiniCssExtractPlugin.loader,
          {
            loader: 'css-loader',
            options: {
              sourceMap: true,
            },
          },
          {
            loader: 'sass-loader',
            options: {
              sourceMap: true,
            },
          },
        ],
      },
    ],
  },
}
