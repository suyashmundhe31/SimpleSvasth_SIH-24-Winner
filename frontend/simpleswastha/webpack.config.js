const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = {
  entry: './src/index.js', // Entry point for your application
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: 'bundle.js',
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader', // Transpiles modern JavaScript
        },
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader'], // Handles CSS files
      },
    ],
  },
  plugins: [
    new HtmlWebpackPlugin({
      template: './public/index.html', // Template for the HTML file
    }),
  ],
  devServer: {
    static: path.join(__dirname, 'dist'),
    compress: true,
    port: 3000, // Port for development server
    hot: true,  // Enable Hot Module Replacement (HMR)
  },
  plugins: [
    new webpack.HotModuleReplacementPlugin()
  ]
};