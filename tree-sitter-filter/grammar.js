/**
 * @file Filter grammar for tree-sitter
 * @author someone
 * @license MIT
 */

export default grammar({
  name: 'filter',
  extras: $ => [/\s/],
  word: $ => $.identifier,
  rules: {
    query: $ => $._expr,
    and_expression: $ => prec.left(2, seq($._expr, 'and', $._expr)),
    _expr: $ => choice(
      $.comparison, $.and_expression, $.or_expression, $.parenthesized,
    ),
    parenthesized: $ => seq('(', $._expr, ')'),    or_expression: $ => prec.left(1, seq($._expr, 'or', $._expr)),    comparison: $ => seq($.identifier, choice('=', '!=', '>', '<', '>=', '<='), $._value),
    _value: $ => choice($.string, $.number),
    string: $ => /"[^"]*"/,
    number: $ => /\d+(\.\d+)?/,
    identifier: $ => /[a-zA-Z_][a-zA-Z0-9_.]*/,
  }
});