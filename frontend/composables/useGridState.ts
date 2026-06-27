import type { GridState } from '~/types/grid'

export function useGridState() {
  const config = useRuntimeConfig()

  const { data, error, refresh } = useAsyncData<GridState>(
    'grid-state',
    () => $fetch<GridState>(`${config.public.apiBaseUrl}/api/state`)
  )

  return { data, error, refresh }
}
