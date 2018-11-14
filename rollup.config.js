import resolve from 'rollup-plugin-node-resolve';
import vue from 'rollup-plugin-vue';
import replace from 'rollup-plugin-replace';
import commonjs from 'rollup-plugin-commonjs';
import babel from 'rollup-plugin-babel';

import pkg from './package.json';

const NODE_ENV = JSON.stringify(process.env.NODE_ENV || 'development');
const VUE_ENV = JSON.stringify(process.env.VUE_ENV || 'browser');

export default {
  input: pkg.entry,
  output: { file: pkg.main, name: 'psd', format: 'iife' },
  plugins: [
    resolve({ browser: true }),
    vue(),
    replace({
      'process.env.NODE_ENV': NODE_ENV,
      'process.env.VUE_ENV': VUE_ENV,
    }),
    commonjs(),
    babel({ exclude: 'node_modules/**' }),
  ],
};
