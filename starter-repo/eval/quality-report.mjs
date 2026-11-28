#!/usr/bin/env node

import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));

function parseCsv(text) {
  const rows = [];
  let row = [];
  let field = "";
  let quoted = false;
  const input = String(text).replace(/^\uFEFF/, "");

  for (let index = 0; index < input.length; index += 1) {
    const char = input[index];
    if (quoted) {
      if (char === '"' && input[index + 1] === '"') {
        field += '"';
        index += 1;
      } else if (char === '"') {
        quoted = false;
      } else {
        field += char;
      }
    } else if (char === '"' && field === "") {
      quoted = true;
    } else if (char === ",") {
      row.push(field);
      field = "";
    } else if (char === "\n" || char === "\r") {
      if (char === "\r" && input[index + 1] === "\n") index += 1;
      row.push(field);
      if (row.some((value) => value !== "")) rows.push(row);
      row = [];
      field = "";
    } else {
      field += char;
    }
  }

  if (quoted) throw new Error("CSV có trường được mở dấu ngoặc kép nhưng chưa đóng.");
  row.push(field);
  if (row.some((value) => value !== "")) rows.push(row);
  return rows;
}

function recordsFromCsv(csv, label, requiredColumns) {
  const rows = parseCsv(csv);
  if (rows.length === 0) throw new Error(`${label} đang trống.`);
  const header = rows[0].map((cell) => cell.trim());
  for (const column of requiredColumns) {
    if (!header.includes(column)) throw new Error(`${label} thiếu cột ${column}.`);
  }
  return rows.slice(1).map((values, index) => {
    if (values.length !== header.length) {
      throw new Error(`${label}, dòng ${index + 2}: số cột không khớp tiêu đề.`);
    }
    return Object.fromEntries(header.map((key, column) => [key, values[column]]));
  });
}

function gradedValue(value, id) {
  const normalized = String(value ?? "").trim().toLowerCase();
  if (!normalized) return null;
  if (["1", "x", "dat", "đạt"].includes(normalized)) return true;
  if (["0", "khong", "không"].includes(normalized)) return false;
  throw new Error(`Ca ${id} có giá trị pass không hợp lệ: ${value}`);
}

function summarize(items) {
  const passed = items.filter((item) => item.pass === true).length;
  const failed = items.filter((item) => item.pass === false).length;
  const unscored = items.filter((item) => item.pass === null).length;
  const scored = passed + failed;
  return {
    total: items.length,
    observed: items.filter((item) => item.observed).length,
    passed,
    failed,
    unscored,
    missing: items.filter((item) => !item.observed).length,
    scored,
    rate: scored === 0 ? null : passed / scored,
  };
}

export function scoreRun(runCsv, metricMapCsv) {
  const mapping = recordsFromCsv(metricMapCsv, "Metric map", ["id", "metric"]);
  const runRows = recordsFromCsv(runCsv, "Run CSV", ["id", "pass"]);
  const mapById = new Map();
  for (const item of mapping) {
    const id = item.id.trim();
    const metric = item.metric.trim();
    if (!id || !metric) throw new Error("Metric map có dòng thiếu id hoặc metric.");
    if (mapById.has(id)) throw new Error(`ID bị trùng trong metric map: ${id}`);
    mapById.set(id, metric);
  }

  const rowsById = new Map();
  const runIds = new Set();
  for (const row of runRows) {
    const id = row.id.trim();
    if (!id) throw new Error("Run CSV có dòng thiếu id.");
    if (rowsById.has(id)) throw new Error(`ID bị trùng trong run CSV: ${id}`);
    if (!mapById.has(id)) throw new Error(`ID không có trong metric map: ${id}`);
    rowsById.set(id, { id, pass: gradedValue(row.pass, id), observed: true, error: row.error ?? "" });
    if (row.run_id?.trim()) runIds.add(row.run_id.trim());
  }
  if (runIds.size > 1) throw new Error("Run CSV chứa nhiều run_id; hãy chấm từng lượt riêng.");

  const items = [...mapById].map(([id, metric]) => ({
    ...(rowsById.get(id) || { id, pass: null, observed: false, error: "" }),
    metric,
  }));
  const groups = [...new Set(mapping.map((item) => item.metric.trim()))].map((metric) => {
    const members = items.filter((item) => item.metric === metric);
    return { metric, ...summarize(members) };
  });

  return {
    runId: [...runIds][0] || "không ghi trong CSV",
    totalCases: items.length,
    overall: summarize(items),
    technicalErrors: items.filter((item) => item.observed && item.error.trim()).length,
    groups,
  };
}

function percent(rate) {
  return rate === null ? "chưa có ca được chấm" : `${(rate * 100).toFixed(1)}%`;
}

export function renderReport(result) {
  const lines = [
    `# Báo cáo chất lượng quan sát được — ${result.runId}`,
    "",
    "> Tỷ lệ dưới đây là tỷ lệ đạt trên bộ ca kiểm thử cố định; không phải độ chính xác lâm sàng và không dự đoán hiệu năng trên phiếu thật.",
    "",
    `- Tổng ca trong metric map: ${result.overall.total}`,
    `- Đã có trong lượt chạy: ${result.overall.observed}/${result.overall.total}; còn thiếu: ${result.overall.missing}`,
    `- Đã chấm: ${result.overall.scored}; đạt: ${result.overall.passed}; không đạt: ${result.overall.failed}; chưa chấm: ${result.overall.unscored}`,
    `- **Tỷ lệ đạt trên bộ ca cố định:** ${result.overall.passed}/${result.overall.scored} (${percent(result.overall.rate)}).`,
    `- Lỗi kỹ thuật: ${result.technicalErrors}`,
    "",
    "| Nhóm ca | Có trong lượt | Đã chấm | Đạt | Không đạt | Chưa chấm | Tỷ lệ đạt trên bộ ca |",
    "|---|---:|---:|---:|---:|---:|---:|",
    ...result.groups.map((group) =>
      `| ${group.metric} | ${group.observed}/${group.total} | ${group.scored} | ${group.passed} | ${group.failed} | ${group.unscored} | ${percent(group.rate)} |`
    ),
    "",
    "Không tính khoảng tin cậy cho bộ ca chủ đích/giả lập này vì nó không phải mẫu đại diện được lấy ngẫu nhiên từ quần thể sử dụng.",
    "",
  ];
  return lines.join("\n");
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const runPath = path.resolve(process.cwd(), process.argv[2] || "eval/run-1.csv");
  const mapPath = path.join(SCRIPT_DIR, "quality-metric-map.csv");
  try {
    const report = scoreRun(readFileSync(runPath, "utf8"), readFileSync(mapPath, "utf8"));
    process.stdout.write(renderReport(report));
  } catch (error) {
    process.stderr.write(`Không thể tạo báo cáo: ${error.message}\n`);
    process.exitCode = 1;
  }
}
