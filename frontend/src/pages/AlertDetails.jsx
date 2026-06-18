import { motion } from "framer-motion";
import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { ChevronLeft, AlertTriangle, ShieldCheck, Clock, MapPin, Search } from "lucide-react";
import { inspectionService, formatDateTime } from "@/services/api";

export default function AlertDetails() {
  const { id } = useParams();
  const [inspection, setInspection] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDetail = async () => {
      try {
        setLoading(true);
        const res = await inspectionService.detail(id);
        setInspection(res.data);
      } catch (err) {
        setError(err.message || "Failed to load details");
      } finally {
        setLoading(false);
      }
    };
    fetchDetail();
  }, [id]);

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center min-h-[50vh]">
        <div className="w-8 h-8 border-4 border-brand-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (error || !inspection) {
    return <div className="p-6 text-red-500 font-medium">Error: {error}</div>;
  }

  const isAlert = inspection.status === "ALERT" || inspection.status === "flagged";
  const processedVideo = inspection.processed_video;
  const videoUrl = processedVideo 
    ? (processedVideo.startsWith('http') ? processedVideo : `${import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'}${processedVideo}`)
    : null;
  const processedImage = inspection.images?.[0]?.processed_image || inspection.images?.[0]?.image;
  const imgUrl = processedImage 
    ? (processedImage.startsWith('http') ? processedImage : `${import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'}${processedImage}`)
    : null;

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="p-6">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <Link to="/history" className="w-10 h-10 bg-white border border-slate-200 rounded-xl flex items-center justify-center text-slate-500 hover:text-slate-800 hover:bg-slate-50 transition-all">
          <ChevronLeft className="w-5 h-5" />
        </Link>
        <div>
          <h1 className="text-3xl font-bold text-slate-800 flex items-center gap-3">
            Inspection Details
            <span className={`text-sm px-3 py-1 rounded-full font-semibold ${isAlert ? "bg-red-100 text-red-700" : "bg-green-100 text-green-700"}`}>
              {inspection.risk_level}
            </span>
          </h1>
          <p className="text-sm text-slate-500 mt-1">ID: SCN-{String(inspection.id).slice(0,8).toUpperCase()}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Image & Detections */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm">
            <h2 className="text-xl font-bold text-slate-800 mb-4 flex items-center gap-2">
              <Search className="w-5 h-5 text-brand-500" />
              Scanned Feed
            </h2>
            <div className="bg-slate-100 rounded-2xl overflow-hidden relative min-h-[300px] flex items-center justify-center">
              {videoUrl ? (
                <video src={videoUrl} controls autoPlay loop muted className="w-full h-auto object-contain max-h-[600px]" />
              ) : imgUrl ? (
                <img src={imgUrl} alt="Processed" className="w-full h-auto object-contain max-h-[600px]" />
              ) : (
                <p className="text-slate-400">No feed media available</p>
              )}
            </div>
          </div>

          <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm">
             <h2 className="text-xl font-bold text-slate-800 mb-4">Detected Objects</h2>
             <div className="space-y-3">
                {inspection.images?.flatMap(i => i.detected_objects)?.length > 0 ? (
                  inspection.images.flatMap(i => i.detected_objects).map((det, idx) => (
                    <div key={idx} className="flex items-start gap-4 p-4 rounded-2xl border border-slate-100 bg-slate-50">
                      <div className="w-10 h-10 rounded-full bg-white flex items-center justify-center flex-shrink-0 text-lg shadow-sm border border-slate-100">
                         {det.severity === 'HIGH' ? '⚠️' : '🔍'}
                      </div>
                      <div className="flex-1">
                         <div className="flex justify-between items-start">
                           <h3 className="font-semibold text-slate-800">{det.raw_label || det.object_type}</h3>
                           <span className="text-xs font-medium text-slate-500 bg-white px-2 py-1 rounded-md border border-slate-200">
                             {(det.confidence * 100).toFixed(1)}% Conf
                           </span>
                         </div>
                         <p className="text-sm text-slate-600 mt-1">{det.gemini_suggestion}</p>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-slate-500">No objects detected.</p>
                )}
             </div>
          </div>
        </div>

        {/* Right Column - Meta Data */}
        <div className="space-y-6">
          <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm">
            <h2 className="text-lg font-bold text-slate-800 mb-5">Metadata</h2>
            
            <div className="space-y-5">
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-xl bg-slate-50 border border-slate-100 flex items-center justify-center text-slate-500">
                  <Clock className="w-5 h-5" />
                </div>
                <div>
                  <p className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Timestamp</p>
                  <p className="text-sm font-medium text-slate-700 mt-0.5">{formatDateTime(inspection.timestamp)}</p>
                </div>
              </div>

              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-xl bg-slate-50 border border-slate-100 flex items-center justify-center text-slate-500">
                  <MapPin className="w-5 h-5" />
                </div>
                <div>
                  <p className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Location / Camera</p>
                  <p className="text-sm font-medium text-slate-700 mt-0.5">{inspection.camera_id}</p>
                </div>
              </div>

              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-xl bg-slate-50 border border-slate-100 flex items-center justify-center text-slate-500">
                  {isAlert ? <AlertTriangle className="w-5 h-5 text-red-500" /> : <ShieldCheck className="w-5 h-5 text-green-500" />}
                </div>
                <div>
                  <p className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Status</p>
                  <p className="text-sm font-medium text-slate-700 mt-0.5 uppercase">{inspection.status}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}