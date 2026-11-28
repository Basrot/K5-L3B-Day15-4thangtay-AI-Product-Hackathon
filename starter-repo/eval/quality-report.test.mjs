import test from "node:test";
import assert from "node:assert/strict";
import { scoreRun, renderReport } from "./quality-report.mjs";

const manifest = `id,metric\nB01,explain\nB02,explain\nB03,boundary\n`;

test("scores only graded cases and preserves quoted multiline CSV fields", () => {
  const run = [
    "run_id,id,output,pass,error",
    'r1,B01,"Answer, with a comma and ""quote""\ncontinued",1,',
    'r1,B02,"Wrong answer",0,',
    'r1,B03,"Not graded",,',
    "",
  ].join("\n");

  const result = scoreRun(run, manifest);
  assert.equal(result.overall.total, 3);
  assert.equal(result.overall.scored, 2);
  assert.equal(result.overall.passed, 1);
  assert.equal(result.overall.unscored, 1);
  assert.equal(result.overall.rate, 0.5);
  assert.deepEqual(result.groups.map((group) => [group.metric, group.scored, group.passed]), [
    ["explain", 2, 1],
    ["boundary", 0, 0],
  ]);
});

test("counts technical errors without changing the behavior score", () => {
  const run = "run_id,id,output,pass,error\nr1,B01,failed,0,Timeout\nr1,B02,ok,1,";
  const result = scoreRun(run, manifest);
  assert.equal(result.technicalErrors, 1);
  assert.equal(result.overall.passed, 1);
  assert.equal(result.overall.scored, 2);
});

test("reports benchmark cases missing from the run instead of dropping them", () => {
  const result = scoreRun("run_id,id,pass,error\nr1,B01,1,", manifest);
  assert.equal(result.overall.total, 3);
  assert.equal(result.overall.observed, 1);
  assert.equal(result.overall.missing, 2);
  assert.equal(result.overall.rate, 1);
});

test("rejects duplicate IDs and IDs absent from the metric map", () => {
  assert.throws(() => scoreRun(
    "run_id,id,pass,error\nr1,B01,1,\nr1,B01,0,",
    manifest,
  ), /trùng.*B01/i);
  assert.throws(() => scoreRun(
    "run_id,id,pass,error\nr1,B99,1,",
    manifest,
  ), /không có trong metric map.*B99/i);
});

test("report labels the result as a fixed-set pass rate, not clinical accuracy", () => {
  const result = scoreRun("run_id,id,pass,error\nr1,B01,1,", manifest);
  const report = renderReport(result);
  assert.match(report, /tỷ lệ đạt trên bộ ca cố định/i);
  assert.match(report, /không phải độ chính xác lâm sàng/i);
  assert.match(report, /chưa chấm/);
});
