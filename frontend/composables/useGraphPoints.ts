const SIZE = 500

interface Point {
  x: number
  y: number
}

export function useGraphPoints() {
  function getPoints(values: number[], minimum: number, range: number): string {
    const width = values.length
    let effectiveRange = range === 0 ? 1 : range

    const points: Point[] = []

    values.forEach((value, index) => {
      const x = Math.round(SIZE * (index + 0.5) / width)
      const y = Math.round(SIZE * (1 - (value - minimum) / effectiveRange))

      if (points.length > 1) {
        const p1 = points[points.length - 2]
        const p2 = points[points.length - 1]
        // Remove collinear middle point
        if ((y - p2.y) * (p2.x - p1.x) === (p2.y - p1.y) * (x - p2.x)) {
          points.pop()
        }
      }

      points.push({ x, y })
    })

    return points.map(p => `${p.x} ${p.y}`).join(' ')
  }

  function getOverlayRects(
    count: number,
    times: number[],
    timeFormat: string,
    valueGroups: string[][],
    decimalPlaces: number
  ): Array<{ x: number; width: number; time: string; values: string }> {
    const { formatDate } = useFormatters()
    return times.map((time, index) => ({
      x: Math.round(SIZE * index / count),
      width: Math.round(SIZE / count),
      time: formatDate(time, timeFormat),
      values: valueGroups[index].map(v => {
        const n = parseFloat(v)
        return isNaN(n) ? v : n.toFixed(decimalPlaces)
      }).join(' ')
    }))
  }

  return { getPoints, getOverlayRects }
}
