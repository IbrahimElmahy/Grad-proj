export default function Toggle({ checked, onChange, label, description }) {
  return (
    <label className="flex items-center justify-between cursor-pointer select-none group">
      {(label || description) && (
        <div>
          {label && <p className="text-sm font-medium text-slate-800">{label}</p>}
          {description && <p className="text-xs text-slate-500 mt-0.5">{description}</p>}
        </div>
      )}
      <div className="relative flex-shrink-0 ml-4">
        <input
          type="checkbox"
          className="sr-only"
          checked={checked}
          onChange={(e) => onChange(e.target.checked)}
        />
        <div
          className={`w-11 h-6 rounded-full transition-colors duration-200 ${
            checked ? 'bg-brand-500' : 'bg-slate-300'
          }`}
        />
        <div
          className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full shadow transition-transform duration-200 ${
            checked ? 'translate-x-5' : 'translate-x-0'
          }`}
        />
      </div>
    </label>
  )
}
