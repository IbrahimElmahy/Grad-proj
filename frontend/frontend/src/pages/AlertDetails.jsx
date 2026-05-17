import { motion } from "framer-motion";
import { useMemo, useState } from "react";

import {
  Search,
  Calendar,
  ExternalLink,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";

const alerts = [
  {
    id: 1,
    title: "Low Visibility Sector A-4",
    desc: "Runway 27L - Fog Density Threshold Exceeded",
    date: "Oct 24, 2023",
    time: "09:15:42",
    severity: "CRITICAL",
    status: "Resolved",
  },

  {
    id: 2,
    title: "Obstacle Detection 09R",
    desc: "Runway Entry - Potential FOD Detected",
    date: "Oct 23, 2023",
    time: "14:30:10",
    severity: "WARNING",
    status: "Archived",
  },

  {
    id: 3,
    title: "Routine Scan - Clear",
    desc: "Southwest Runway Visibility Clear",
    date: "Oct 23, 2023",
    time: "12:00:00",
    severity: "SAFE",
    status: "Archived",
  },

  {
    id: 4,
    title: "Heavy Fog Warning",
    desc: "Meteorological Alert - Operations Suspended",
    date: "Oct 22, 2023",
    time: "15:48:19",
    severity: "CRITICAL",
    status: "Resolved",
  },

  {
    id: 5,
    title: "Sensor Calibration Check",
    desc: "Scheduled maintenance of IR arrays",
    date: "Oct 22, 2023",
    time: "10:00:22",
    severity: "SAFE",
    status: "Archived",
  },

  {
    id: 6,
    title: "Camera Signal Lost",
    desc: "North Runway Camera Disconnected",
    date: "Oct 21, 2023",
    time: "07:10:12",
    severity: "WARNING",
    status: "Resolved",
  },

  {
    id: 7,
    title: "Emergency Scan",
    desc: "Manual runway inspection completed",
    date: "Oct 20, 2023",
    time: "16:42:30",
    severity: "SAFE",
    status: "Archived",
  },
];

const ITEMS_PER_PAGE = 5;

export default function HistoryPage() {
  const [search, setSearch] = useState("");

  const [severityFilter, setSeverityFilter] =
    useState("ALL");

  const [currentPage, setCurrentPage] = useState(1);

  const [data, setData] = useState(alerts);

  // Filter + Search
  const filteredData = useMemo(() => {
    return data.filter((item) => {
      const matchesSearch =
        item.title
          .toLowerCase()
          .includes(search.toLowerCase()) ||
        item.desc
          .toLowerCase()
          .includes(search.toLowerCase());

      const matchesSeverity =
        severityFilter === "ALL" ||
        item.severity === severityFilter;

      return matchesSearch && matchesSeverity;
    });
  }, [search, severityFilter, data]);

  // Pagination
  const totalPages = Math.ceil(
    filteredData.length / ITEMS_PER_PAGE
  );

  const paginatedData = filteredData.slice(
    (currentPage - 1) * ITEMS_PER_PAGE,
    currentPage * ITEMS_PER_PAGE
  );

  // Export CSV
  const exportCSV = () => {
    const csv = [
      ["Title", "Severity", "Status"],

      ...filteredData.map((item) => [
        item.title,
        item.severity,
        item.status,
      ]),
    ]
      .map((e) => e.join(","))
      .join("\n");

    const blob = new Blob([csv], {
      type: "text/csv",
    });

    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");

    a.href = url;

    a.download = "history-report.csv";

    a.click();
  };

  // Refresh
  const refreshData = () => {
    setData([...alerts]);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="p-6"
    >
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-6">
        <div>
          <h1 className="text-3xl font-bold text-slate-800">
            System History
          </h1>

          <p className="text-sm text-slate-500 mt-1">
            Audit log of runway visibility events and
            automated scans.
          </p>
        </div>

        <div className="flex gap-3">
          {/* Export */}
          <button
            onClick={exportCSV}
            className="bg-white border border-slate-200 hover:bg-slate-50 px-4 py-2 rounded-xl text-sm font-medium text-slate-700 transition-all"
          >
            Export Report
          </button>

          {/* Refresh */}
          <button
            onClick={refreshData}
            className="bg-brand-500 hover:bg-brand-600 text-white px-4 py-2 rounded-xl text-sm font-medium transition-all"
          >
            Refresh Data
          </button>
        </div>
      </div>

      {/* Search + Filters */}
      <div className="bg-white rounded-2xl border border-slate-200 p-4 mb-6 shadow-sm">
        <div className="flex flex-col lg:flex-row gap-3">
          {/* Search */}
          <div className="flex-1 relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-4 top-1/2 -translate-y-1/2" />

            <input
              type="text"
              placeholder="Search alert title..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setCurrentPage(1);
              }}
              className="w-full bg-slate-50 border border-slate-200 rounded-xl pl-11 pr-4 py-3 text-sm outline-none focus:ring-2 focus:ring-brand-500"
            />
          </div>

          {/* Date */}
          <button className="flex items-center gap-2 bg-slate-50 border border-slate-200 px-4 py-3 rounded-xl text-sm text-slate-700 hover:bg-slate-100 transition-all">
            <Calendar className="w-4 h-4" />
            Oct 20, 2023 - Oct 27, 2023
          </button>

          {/* Filter */}
          <select
            value={severityFilter}
            onChange={(e) => {
              setSeverityFilter(e.target.value);
              setCurrentPage(1);
            }}
            className="bg-slate-50 border border-slate-200 px-4 py-3 rounded-xl text-sm outline-none"
          >
            <option value="ALL">All</option>

            <option value="CRITICAL">
              Critical
            </option>

            <option value="WARNING">
              Warning
            </option>

            <option value="SAFE">Safe</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr className="text-left">
                <th className="px-6 py-4 text-[12px] uppercase tracking-wider text-slate-500">
                  Alert Title
                </th>

                <th className="px-6 py-4 text-[12px] uppercase tracking-wider text-slate-500">
                  Date & Time
                </th>

                <th className="px-6 py-4 text-[12px] uppercase tracking-wider text-slate-500">
                  Severity
                </th>

                <th className="px-6 py-4 text-[12px] uppercase tracking-wider text-slate-500">
                  Status
                </th>

                <th className="px-6 py-4 text-[12px] uppercase tracking-wider text-slate-500">
                  Action
                </th>
              </tr>
            </thead>

            <tbody>
              {paginatedData.map((alert, index) => (
                <motion.tr
                  key={alert.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{
                    delay: index * 0.05,
                  }}
                  className="border-b border-slate-100 hover:bg-slate-50 transition-all"
                >
                  {/* Alert */}
                  <td className="px-6 py-5">
                    <div>
                      <h3 className="font-semibold text-slate-800 text-sm">
                        {alert.title}
                      </h3>

                      <p className="text-[12px] text-slate-500 mt-1">
                        {alert.desc}
                      </p>
                    </div>
                  </td>

                  {/* Date */}
                  <td className="px-6 py-5">
                    <div>
                      <p className="text-sm font-medium text-slate-700">
                        {alert.date}
                      </p>

                      <p className="text-[12px] text-slate-500 mt-1">
                        {alert.time}
                      </p>
                    </div>
                  </td>

                  {/* Severity */}
                  <td className="px-6 py-5">
                    <span
                      className={`px-3 py-1 rounded-full text-[11px] font-semibold ${
                        alert.severity ===
                        "CRITICAL"
                          ? "bg-red-100 text-red-700"
                          : alert.severity ===
                            "WARNING"
                          ? "bg-yellow-100 text-yellow-700"
                          : "bg-green-100 text-green-700"
                      }`}
                    >
                      {alert.severity}
                    </span>
                  </td>

                  {/* Status */}
                  <td className="px-6 py-5">
                    <span className="text-sm text-slate-600">
                      • {alert.status}
                    </span>
                  </td>

                  {/* Action */}
                  <td className="px-6 py-5">
                    <button className="text-brand-500 hover:text-brand-700 transition-all">
                      <ExternalLink className="w-4 h-4" />
                    </button>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="flex items-center justify-between px-6 py-4">
          <p className="text-sm text-slate-500">
            Showing{" "}
            {(currentPage - 1) * ITEMS_PER_PAGE + 1}
            -
            {Math.min(
              currentPage * ITEMS_PER_PAGE,
              filteredData.length
            )}{" "}
            of {filteredData.length} alerts
          </p>

          <div className="flex items-center gap-2">
            {/* Prev */}
            <button
              onClick={() =>
                setCurrentPage((prev) =>
                  Math.max(prev - 1, 1)
                )
              }
              className="w-9 h-9 rounded-lg border border-slate-200 flex items-center justify-center hover:bg-slate-50"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>

            {/* Current */}
            <button className="w-9 h-9 rounded-lg bg-brand-500 text-white text-sm font-medium">
              {currentPage}
            </button>

            {/* Next */}
            <button
              onClick={() =>
                setCurrentPage((prev) =>
                  Math.min(
                    prev + 1,
                    totalPages
                  )
                )
              }
              className="w-9 h-9 rounded-lg border border-slate-200 flex items-center justify-center hover:bg-slate-50"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Bottom Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
        {/* Card */}
        <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
          <p className="text-[11px] uppercase tracking-wider text-slate-500 font-semibold mb-2">
            Critical Events
          </p>

          <h2 className="text-3xl font-bold text-slate-800">
            {
              data.filter(
                (item) =>
                  item.severity ===
                  "CRITICAL"
              ).length
            }
          </h2>

          <p className="text-sm text-red-500 mt-2">
            Live statistics
          </p>
        </div>

        {/* Card */}
        <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
          <p className="text-[11px] uppercase tracking-wider text-slate-500 font-semibold mb-2">
            Total Scans
          </p>

          <h2 className="text-3xl font-bold text-slate-800">
            {data.length}
          </h2>

          <p className="text-sm text-slate-500 mt-2">
            Loaded history records
          </p>
        </div>

        {/* Card */}
        <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
          <p className="text-[11px] uppercase tracking-wider text-slate-500 font-semibold mb-2">
            Resolved Cases
          </p>

          <h2 className="text-3xl font-bold text-green-600">
            {
              data.filter(
                (item) =>
                  item.status ===
                  "Resolved"
              ).length
            }
          </h2>

          <p className="text-sm text-green-500 mt-2">
            Successfully resolved
          </p>
        </div>
      </div>
    </motion.div>
  );
}