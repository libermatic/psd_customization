// Copyright (c) 2018, Libermatic and contributors
// For license information, please see license.txt

const colorPresets = [
  '#7cd6fd',
  '#5e64ff',
  '#743ee2',
  '#ff5858',
  '#ffa00a',
  '#feef72',
  '#28a745',
  '#98d85b',
  '#b554ff',
  '#ffa3ef',
];

export function colorHash(str) {
  if (!str) {
    return '#b8c2cc';
  }
  return colorPresets[
    str.split('').reduce((a, x) => a + x.charCodeAt(0), 0) % colorPresets.length
  ];
}

export default { colorHash };
