const { ModuleFederationPlugin } = require('@module-federation/webpack-plugin');
const deps = require('./package.json').dependencies;

module.exports = {
  mode: 'development',
  devServer: {
    port: 3003,
    historyApiFallback: true,
  },
  plugins: [
    new ModuleFederationPlugin({
      name: 'admin',
      filename: 'remoteEntry.js',
      exposes: {
        './App': './src/App',
        './Dashboard': './src/components/Dashboard',
        './UserManagement': './src/components/UserManagement',
        './ConversationManagement': './src/components/ConversationManagement',
        './Analytics': './src/components/Analytics',
        './RealTimeAnalytics': './src/components/RealTimeAnalytics',
        './Settings': './src/components/Settings',
      },
      shared: {
        ...deps,
        react: {
          singleton: true,
          requiredVersion: deps.react,
        },
        'react-dom': {
          singleton: true,
          requiredVersion: deps['react-dom'],
        },
        'react-router-dom': {
          singleton: true,
          requiredVersion: deps['react-router-dom'],
        },
      },
    }),
  ],
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        use: 'ts-loader',
        exclude: /node_modules/,
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader'],
      },
    ],
  },
  resolve: {
    extensions: ['.tsx', '.ts', '.js'],
  },
  output: {
    publicPath: 'auto',
  },
};