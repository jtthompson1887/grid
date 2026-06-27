export function useFormatters() {
  function formatPower(value: number): string {
    return _format(value, 2)
  }

  function formatTotalPower(value: number): string {
    return _format(value, 1)
  }

  function formatPercentage(value: number): string {
    return _format(100 * value, 1)
  }

  function formatPrice(value: number): string {
    return _format(value, 2, '£')
  }

  function formatVisits(value: number): string {
    return Math.round(value).toLocaleString()
  }

  function _format(value: number, decimalPlaces: number, prefix = ''): string {
    const sign = value < 0 ? '−' : ''
    return `${sign}${prefix}${Math.abs(value).toFixed(decimalPlaces)}`
  }

  function formatTime(timestamp: number): { datetime: string; display: string; ampm: string } {
    const d = new Date(timestamp * 1000)
    const datetime = d.toISOString().replace(/\.\d{3}Z$/, 'Z')
    const hours = d.getUTCHours()
    const minutes = d.getUTCMinutes().toString().padStart(2, '0')
    const ampm = hours >= 12 ? 'pm' : 'am'
    const h = hours % 12 || 12
    return { datetime, display: `${h}:${minutes}`, ampm }
  }

  function formatDate(timestamp: number, format: string): string {
    const d = new Date(timestamp * 1000)
    if (format === 'g:ia') {
      const hours = d.getUTCHours()
      const minutes = d.getUTCMinutes().toString().padStart(2, '0')
      const ampm = hours >= 12 ? 'am' : 'pm'
      const h = hours % 12 || 12
      return `${h}:${minutes}${ampm}`
    }
    if (format === 'l') {
      return d.toLocaleDateString('en-GB', { weekday: 'long', timeZone: 'UTC' })
    }
    if (format === 'd/m/Y') {
      return d.toLocaleDateString('en-GB', { day: '2-digit', month: '2-digit', year: 'numeric', timeZone: 'UTC' })
    }
    if (format === 'Y') {
      return d.getUTCFullYear().toString()
    }
    if (format === 'jS F Y') {
      const day = d.getUTCDate()
      const suffix = ['th', 'st', 'nd', 'rd'][(day % 100 > 10 && day % 100 < 20) ? 0 : Math.min(day % 10, 3)] || 'th'
      const month = d.toLocaleDateString('en-GB', { month: 'long', timeZone: 'UTC' })
      return `${day}${suffix} ${month} ${d.getUTCFullYear()}`
    }
    return d.toISOString()
  }

  return { formatPower, formatTotalPower, formatPercentage, formatPrice, formatVisits, formatTime, formatDate }
}
