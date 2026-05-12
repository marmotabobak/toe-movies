import { createContext, useContext, useReducer } from 'react'

const Ctx = createContext(null)

function reducer(state, action) {
  const next = new Set(state)
  switch (action.type) {
    case 'TOGGLE':
      next.has(action.id) ? next.delete(action.id) : next.add(action.id)
      return next
    case 'SELECT_ALL':
      return new Set(action.ids)
    case 'CLEAR':
      return new Set()
    default:
      return state
  }
}

export function SelectionProvider({ children }) {
  const [selected, dispatch] = useReducer(reducer, new Set())
  return <Ctx.Provider value={{ selected, dispatch }}>{children}</Ctx.Provider>
}

export function useSelection() {
  const { selected, dispatch } = useContext(Ctx)
  return {
    selected,
    toggle: (id) => dispatch({ type: 'TOGGLE', id }),
    selectAll: (ids) => dispatch({ type: 'SELECT_ALL', ids }),
    clear: () => dispatch({ type: 'CLEAR' }),
  }
}
