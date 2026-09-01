#!/usr/bin/env node
"use strict";

const fs = require("fs");
const vm = require("vm");

if (process.argv.length !== 3) {
  process.stderr.write("usage: run_parser.js PARSER.js\n");
  process.exit(2);
}

const context = vm.createContext({Math, Number, RegExp, isFinite});
vm.runInContext(fs.readFileSync(process.argv[2], "utf8"), context, {filename: process.argv[2]});
const frames = JSON.parse(fs.readFileSync(0, "utf8"));
if (!Array.isArray(frames)) throw new Error("stdin must be a JSON array");
process.stdout.write(JSON.stringify(frames.map(frame => context.parse(frame))) + "\n");
