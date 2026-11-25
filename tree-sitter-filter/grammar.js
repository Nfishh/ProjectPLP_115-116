/**
 * @file Filter grammar for tree-sitter
 * @author someone
 * @license MIT
 */

/// <reference types="tree-sitter-cli/dsl" />
// @ts-check

export default grammar({
  name: "filter",

  rules: {
    // TODO: add the actual grammar rules
    source_file: $ => "hello"
  }
});
