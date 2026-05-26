import { useEffect, useState } from 'react'
import './index.css'

interface Emission {
  id: string
  tenant_name: string
  source_name: string
  scope: number
  category: string
  emission_date: string
  quantity: number
  unit: string
  co2e: number
  status: string
  validation_errors: string[] | null
}

function App() {
  const [emissions, setEmissions] = useState<Emission[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const fetchEmissions = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/emissions/')
      if (!res.ok) throw new Error('Failed to fetch data')
      const data = await res.json()
      setEmissions(data)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchEmissions()
  }, [])

  const handleApprove = async (id: string) => {
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/emissions/${id}/approve/`, {
        method: 'POST',
      })
      if (!res.ok) throw new Error('Failed to approve')
      fetchEmissions()
    } catch (err: any) {
      alert(err.message)
    }
  }

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 tracking-tight">ESG Data Review Queue</h1>
            <p className="text-gray-500 mt-1">Review and approve ingested emissions data before final audit.</p>
          </div>
          <div className="bg-white px-4 py-2 rounded-lg shadow-sm border border-gray-200">
            <span className="text-sm font-medium text-gray-500">Pending Review</span>
            <span className="ml-3 text-lg font-bold text-indigo-600">
              {emissions.filter(e => e.status === 'PENDING_REVIEW').length}
            </span>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border-l-4 border-red-400 p-4 mb-8">
            <p className="text-red-700">{error}</p>
          </div>
        )}

        <div className="bg-white shadow-sm ring-1 ring-gray-900/5 sm:rounded-xl overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900">Source</th>
                <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Category</th>
                <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Date</th>
                <th className="px-3 py-3.5 text-right text-sm font-semibold text-gray-900">Quantity</th>
                <th className="px-3 py-3.5 text-right text-sm font-semibold text-gray-900">CO2e</th>
                <th className="px-3 py-3.5 text-center text-sm font-semibold text-gray-900">Status</th>
                <th className="px-3 py-3.5 text-center text-sm font-semibold text-gray-900">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 bg-white">
              {loading ? (
                <tr><td colSpan={7} className="py-8 text-center text-gray-500">Loading data...</td></tr>
              ) : emissions.length === 0 ? (
                <tr><td colSpan={7} className="py-8 text-center text-gray-500">No records found.</td></tr>
              ) : (
                emissions.map((e) => (
                  <tr key={e.id} className={e.validation_errors ? "bg-red-50/50" : "hover:bg-gray-50"}>
                    <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm">
                      <div className="font-medium text-gray-900">{e.source_name}</div>
                      <div className="text-gray-500 text-xs mt-0.5">Scope {e.scope}</div>
                    </td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{e.category}</td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{e.emission_date}</td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-right font-mono">
                      {e.quantity.toLocaleString()} <span className="text-gray-400">{e.unit}</span>
                    </td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-right font-mono font-medium text-gray-900">
                      {e.co2e.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}
                    </td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-center">
                      {e.validation_errors ? (
                        <div className="inline-flex items-center rounded-md bg-red-50 px-2 py-1 text-xs font-medium text-red-700 ring-1 ring-inset ring-red-600/10">
                          Needs Fix
                        </div>
                      ) : e.status === 'APPROVED' ? (
                        <div className="inline-flex items-center rounded-md bg-green-50 px-2 py-1 text-xs font-medium text-green-700 ring-1 ring-inset ring-green-600/20">
                          Approved
                        </div>
                      ) : (
                        <div className="inline-flex items-center rounded-md bg-yellow-50 px-2 py-1 text-xs font-medium text-yellow-800 ring-1 ring-inset ring-yellow-600/20">
                          Pending
                        </div>
                      )}
                    </td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-center">
                       {e.status !== 'APPROVED' && (
                         <button
                           onClick={() => handleApprove(e.id)}
                           className="text-indigo-600 hover:text-indigo-900 font-medium bg-indigo-50 hover:bg-indigo-100 px-3 py-1.5 rounded transition-colors"
                         >
                           Approve
                         </button>
                       )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        
        {/* Error Details Section for flagged rows */}
        {emissions.some(e => e.validation_errors) && (
          <div className="mt-8 bg-white shadow-sm ring-1 ring-gray-900/5 sm:rounded-xl p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Validation Issues</h2>
            <ul className="space-y-3">
              {emissions.filter(e => e.validation_errors).map(e => (
                <li key={`err-${e.id}`} className="flex items-start text-sm">
                  <span className="text-red-500 mr-2">⚠</span>
                  <div>
                    <span className="font-medium text-gray-900">{e.source_name}</span> ({e.category}): 
                    <span className="text-red-600 ml-1">{e.validation_errors?.join(', ')}</span>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
