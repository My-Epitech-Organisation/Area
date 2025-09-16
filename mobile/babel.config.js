module.exports = function(api) {
  api.cache(true);
  return {
    presets: ['babel-preset-expo'],
    plugins: [
      'react-native-paper/babel',
    ],
    env: {
      development: {
        plugins: [
          '@babel/plugin-transform-react-jsx-source',
        ],
      },
      production: {
        plugins: ['react-native-paper/babel'],
      },
    },
  };
};
