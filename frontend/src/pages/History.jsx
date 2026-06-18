import { motion } from "framer-motion";
import { useMemo, useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  Search,
  ExternalLink,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { alertsService, formatDateTime } from "@/services/api";

const ITEMS_PER_PAGE = 5;

export default function HistoryPage() {
  const [search, setSearch] = useState("");
  const [severityFilter, setSeverityFilter] = useState("ALL");
  const [currentPage, setCurrentPage] = useState(1);
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      const res = await alertsService.getAll();
      setData(res.data);
    } catch (err) {
      setError(err.message || "Failed to fetch history");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  // Filter + Search
  const filteredData = useMemo(() => {
    return data.filter((item) => {
      const matchesSearch =
        item.title?.toLowerCase().includes(search.toLowerCase()) ||
        item.desc?.toLowerCase().includes(search.toLowerCase()) ||
        item.location?.toLowerCase().includes(search.toLowerCase());

      const itemSeverity = item.severity?.toUpperCase() || "SAFE";
      const matchesSeverity =
        severityFilter === "ALL" || itemSeverity === severityFilter;

      return matchesSearch && matchesSeverity;
    });
  }, [search, severityFilter, data]);

  // Pagination
  const totalPages = Math.ceil(filteredData.length / ITEMS_PER_PAGE);

  const paginatedData = filteredData.slice(
    (currentPage - 1) * ITEMS_PER_PAGE,
    currentPage * ITEMS_PER_PAGE
  );

  // Export CSV
  const exportCSV = () => {
    const csv = [
      ["Title", "Description", "Location", "Timestamp", "Severity", "Status"],
      ...filteredData.map((item) => [
        item.title,
        item.desc,
        item.location,
        item.timestamp,
        item.severity?.toUpperCase(),
        item.status || item.inspectionStatus,
      ]),
    ]
      .map((e) => e.map(val => `"${String(val).replace(/"/g, '""')}"`).join(","))
      .join("\n");

    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `history-report-${new Date().toISOString().slice(0,10)}.csv`;
    a.click();
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
            Audit log of runway visibility events and automated scans.
          </p>
        </div>

        <div className="flex gap-3">
          <button
            onClick={exportCSV}
            className="bg-white border border-slate-200 hover:bg-slate-50 px-4 py-2 rounded-xl text-sm font-medium text-slate-700 transition-all shadow-sm"
          >
            Export Report
          </button>

          <button
            onClick={fetchHistory}
            className="bg-brand-500 hover:bg-brand-600 text-white px-4 py-2 rounded-xl text-sm font-medium transition-all shadow-sm"
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
              placeholder="Search alert title, description or location..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setCurrentPage(1);
              }}
              className="w-full bg-slate-50 border border-slate-200 rounded-xl pl-11 pr-4 py-3 text-sm outline-none focus:ring-2 focus:ring-brand-500 transition-all"
            />
          </div>

          {/* Filter */}
          <select
            value={severityFilter}
            onChange={(e) => {
              setSeverityFilter(e.target.value);
              setCurrentPage(1);
            }}
            className="bg-slate-50 border border-slate-200 px-4 py-3 rounded-xl text-sm outline-none focus:ring-2 focus:ring-brand-500 transition-all"
          >
            <option value="ALL">All Severities</option>
            <option value="CRITICAL">Critical</option>
            <option value="WARNING">Warning</option>
            <option value="SAFE">Safe</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
        {loading ? (
          <div className="p-12 flex justify-center items-center">
            <div className="w-8 h-8 border-4 border-brand-500 border-t-transparent rounded-full animate-spin"></div>
          </div>
        ) : error ? (
          <div className="p-12 text-center text-red-500 font-medium">
            Error: {error}
          </div>
        ) : paginatedData.length === 0 ? (
          <div className="p-12 text-center text-slate-500">
            No records found matching your filters.
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-slate-50 border-b border-slate-200">
                  <tr className="text-left">
                    <th className="px-6 py-4 text-[12px] uppercase tracking-wider text-slate-500">
                      Alert / Event
                    </th>
                    <th className="px-6 py-4 text-[12px] uppercase tracking-wider text-slate-500">
                      Date & Time
                    </th>
                    <th className="px-6 py-4 text-[12px] uppercase tracking-wider text-slate-500">
                      Severity
                    </th>
                    <th className="px-6 py-4 text-[12px] uppercase tracking-wider text-slate-500">
                      Location
                    </th>
                    <th className="px-6 py-4 text-[12px] uppercase tracking-wider text-slate-500">
                      Action
                    </th>
                  </tr>
                </thead>

                <tbody>
                  {paginatedData.map((alert, index) => {
                    const sev = alert.severity?.toUpperCase() || "SAFE";
                    return (
                      <motion.tr
                        key={alert.id}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.05 }}
                        className="border-b border-slate-100 hover:bg-slate-50 transition-all"
                      >
                        {/* Alert */}
                        <td className="px-6 py-5">
                          <div>
                            <h3 className="font-semibold text-slate-800 text-sm">
                              {alert.title}
                            </h3>
                            <p className="text-[12px] text-slate-500 mt-1 max-w-md truncate">
                              {alert.desc}
                            </p>
                          </div>
                        </td>

                        {/* Date */}
                        <td className="px-6 py-5 text-sm text-slate-600">
                          {formatDateTime(alert.timestamp)}
                        </td>

                        {/* Severity */}
                        <td className="px-6 py-5">
                          <span
                            className={`px-3 py-1 rounded-full text-[11px] font-semibold ${
                              sev === "CRITICAL"
                                ? "bg-red-100 text-red-700"
                                : sev === "WARNING"
                                ? "bg-yellow-100 text-yellow-700"
                                : "bg-green-100 text-green-700"
                            }`}
                          >
                            {sev}
                          </span>
                        </td>

                        {/* Location */}
                        <td className="px-6 py-5 text-sm text-slate-600">
                          {alert.location}
                        </td>

                        {/* Action */}
                        <td className="px-6 py-5">
                          <Link
                            to={`/alerts/${alert.id}`}
                            className="text-brand-500 hover:text-brand-700 transition-all flex items-center gap-1 text-sm font-medium"
                          >
                            Details
                            <ExternalLink className="w-3.5 h-3.5" />
                          </Link>
                        </td>
                      </motion.tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div className="flex items-center justify-between px-6 py-4 border-t border-slate-100">
              <p className="text-sm text-slate-500">
                Showing {" "}
                {(currentPage - 1) * ITEMS_PER_PAGE + 1}
                -
                {Math.min(currentPage * ITEMS_PER_PAGE, filteredData.length)}{" "}
                of {filteredData.length} entries
              </p>

              <div className="flex items-center gap-2">
                <button
                  disabled={currentPage === 1}
                  onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
                  className="w-9 h-9 rounded-lg border border-slate-200 flex items-center justify-center hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>

                <button className="w-9 h-9 rounded-lg bg-brand-500 text-white text-sm font-medium">
                  {currentPage}
                </button>

                <button
                  disabled={currentPage === totalPages || totalPages === 0}
                  onClick={() => setCurrentPage((prev) => Math.min(prev + 1, totalPages))}
                  className="w-9 h-9 rounded-lg border border-slate-200 flex items-center justify-center hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </motion.div>
  );
}