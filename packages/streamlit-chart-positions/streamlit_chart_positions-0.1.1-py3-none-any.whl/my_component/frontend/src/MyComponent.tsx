"use client"

import { Streamlit, withStreamlitConnection, type ComponentProps } from "streamlit-component-lib"
import { useCallback, useEffect, useMemo, useState, type ReactElement } from "react"

// Constants for the default grid size
const DEFAULT_ROWS = 7
const DEFAULT_COLS = 3

// Function to clean position format (remove modifiers)
const cleanPositionFormat = (position: string): string => {
  return position
    .replace(/$$Auto Select$$/g, "")
    .replace(/$$Disabled$$/g, "")
    .replace(/red/g, "") // Also handle 'red' if it's used as a modifier
    .replace(/FULL ROW \d+/g, "") // Remove FULL ROW modifier if it somehow appears
    .trim()
}

interface Position {
  id: string // Original ID from input
  cleanId: string // Cleaned ID for display and return
  row: number
  col: number // col will always be a number now
  isAutoSelect: boolean
  isDisabled: boolean
  // isFullRow: boolean; // Removed as full row functionality is removed
}

function MyComponent({ args, disabled, theme }: ComponentProps): ReactElement {
  const { positions = [] } = args

  // Map input positions for quick lookup
  const inputPositionsMap = useMemo(() => {
    const map = new Map<string, string>()
    positions.forEach((pos: string) => {
      // Ensure we only map column-based positions, ignore any old full row inputs
      const cleaned = cleanPositionFormat(pos)
      if (cleaned.includes("ROW") && cleaned.includes("COL")) {
        map.set(cleaned, pos)
      }
    })
    return map
  }, [positions])

  // Generate all possible grid positions (7x3) and apply properties from input
  const allGridPositions = useMemo(() => {
    const grid: Position[] = []
    for (let r = 1; r <= DEFAULT_ROWS; r++) {
      for (let c = 1; c <= DEFAULT_COLS; c++) {
        const colCleanId = `ROW${r}, COL${c}`
        const inputColString = inputPositionsMap.get(colCleanId)

        if (inputColString) {
          // Column was explicitly passed
          grid.push({
            id: inputColString,
            cleanId: colCleanId,
            row: r,
            col: c,
            isAutoSelect: inputColString.includes("(Auto Select)"),
            isDisabled: inputColString.includes("(Disabled)") || inputColString.includes("red"),
            // isFullRow: false, // Always false now
          })
        } else {
          // Column was NOT explicitly passed, so it's disabled by default
          grid.push({
            id: colCleanId, // Use cleanId as id for unpassed positions
            cleanId: colCleanId,
            row: r,
            col: c,
            isAutoSelect: false,
            isDisabled: true, // Default to disabled if not passed
            // isFullRow: false, // Always false now
          })
        }
      }
    }
    return grid
  }, [inputPositionsMap])

  // State to manage selected positions (using clean IDs)
  const [selectedPositions, setSelectedPositions] = useState<Set<string>>(() => {
    const autoSelectPositions = allGridPositions.filter((pos) => pos.isAutoSelect).map((pos) => pos.cleanId)
    return new Set(autoSelectPositions)
  })

  // Initialize selected positions with auto-select positions
  useEffect(() => {
    const autoSelectPositions = allGridPositions.filter((pos) => pos.isAutoSelect).map((pos) => pos.cleanId)
    setSelectedPositions((prev) => {
      const newSet = new Set(prev)
      autoSelectPositions.forEach((pos) => newSet.add(pos))
      return newSet
    })
  }, [allGridPositions])

  // Send selected positions back to Streamlit (cleaned format)
  useEffect(() => {
    Streamlit.setComponentValue(Array.from(selectedPositions))
  }, [selectedPositions])

  // Set frame height
  useEffect(() => {
    Streamlit.setFrameHeight(700)
  }, [])

  // Toggle position selection
  const togglePosition = useCallback(
    (position: Position) => {
      if (position.isDisabled) return

      const cleanId = position.cleanId
      const clickedRow = position.row

      setSelectedPositions((prevSelected) => {
        const newSelected = new Set(prevSelected)

        // Determine the row of currently selected positions
        let currentSelectedRow: number | null = null
        for (const id of newSelected) {
          const p = allGridPositions.find((gp) => gp.cleanId === id)
          if (p) {
            if (currentSelectedRow === null) {
              currentSelectedRow = p.row
            } else if (currentSelectedRow !== p.row) {
              // Multiple rows already selected, clear them all
              newSelected.clear()
              newSelected.add(cleanId) // Add the newly clicked position
              return newSelected
            }
          }
        }

        // If selections exist in a different row, clear them all
        if (currentSelectedRow !== null && currentSelectedRow !== clickedRow) {
          newSelected.clear()
          newSelected.add(cleanId) // Add the newly clicked position
          return newSelected
        }

        const currentSelectedColsInClickedRow = Array.from(newSelected)
          .filter((id) => {
            const p = allGridPositions.find((gp) => gp.cleanId === id)
            return p && p.row === clickedRow
          })
          .map((id) => allGridPositions.find((gp) => gp.cleanId === id)!.col)

        if (newSelected.has(cleanId)) {
          // Deselecting a column
          newSelected.delete(cleanId)
          const remainingCols = currentSelectedColsInClickedRow.filter((col) => col !== position.col)

          if (remainingCols.length > 0) {
            const sortedCols = [...remainingCols].sort((a, b) => a - b)
            let isContiguous = true
            for (let i = 0; i < sortedCols.length - 1; i++) {
              if (sortedCols[i + 1] - sortedCols[i] !== 1) {
                isContiguous = false
                break
              }
            }
            if (!isContiguous) {
              // If deselecting breaks contiguity, clear all selections in this row
              allGridPositions.forEach((p) => {
                if (p.row === clickedRow) {
                  newSelected.delete(p.cleanId)
                }
              })
            }
          }
        } else {
          // Selecting a column
          newSelected.add(cleanId)
          const allColsInRow = Array.from(newSelected)
            .filter((id) => {
              const p = allGridPositions.find((gp) => gp.cleanId === id)
              return p && p.row === clickedRow
            })
            .map((id) => allGridPositions.find((gp) => gp.cleanId === id)!.col)

          if (allColsInRow.length > 0) {
            const minCol = Math.min(...allColsInRow)
            const maxCol = Math.max(...allColsInRow)
            for (let c = minCol; c <= maxCol; c++) {
              const targetPos = allGridPositions.find((p) => p.row === clickedRow && p.col === c)
              // Only add if it's a valid position and not disabled
              if (targetPos && !targetPos.isDisabled) {
                newSelected.add(targetPos.cleanId)
              }
            }
          }
        }
        return newSelected
      })
    },
    [allGridPositions],
  )

  // Get position status for styling
  const getPositionStatus = (position: Position) => {
    const cleanId = position.cleanId
    if (position.isDisabled) return "disabled"
    if (selectedPositions.has(cleanId)) return "selected"
    return "available"
  }

  // Create grid cells
  const renderGrid = () => {
    const rows = []

    for (let row = 1; row <= DEFAULT_ROWS; row++) {
      const rowPositions = allGridPositions.filter((pos) => pos.row === row)
      const cols = []
      for (let col = 1; col <= DEFAULT_COLS; col++) {
        const position = rowPositions.find((pos) => pos.col === col)
        if (position) {
          const status = getPositionStatus(position)
          cols.push(
            <div key={`${row}-${col}`} className={`position-cell ${status}`} onClick={() => togglePosition(position)}>
              <div className="position-content">
                <span className="position-label">
                  ROW{position.row}, COL{position.col}
                </span>
              </div>
            </div>,
          )
        } else {
          // This case should not be hit if allGridPositions is correctly populated for 7x3
          // but as a fallback, render an empty disabled cell
          cols.push(
            <div key={`${row}-${col}`} className="position-cell empty disabled">
              <div className="position-content">
                <span className="position-label">N/A</span>
              </div>
            </div>,
          )
        }
      }
      rows.push(
        <div key={`row-${row}`} className="grid-row">
          {cols}
        </div>,
      )
    }

    return rows
  }

  const styles = `
    .position-selector {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
      padding: 24px;
      background: #f0f2f6; /* Light gray background */
      min-height: 100vh;
      color: #2d3748;
    }
    
    .container {
      max-width: 1000px;
      margin: 0 auto;
      background: rgba(255, 255, 255, 0.95);
      backdrop-filter: blur(10px);
      border-radius: 20px;
      padding: 32px;
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
    }
    
    .header {
      margin-bottom: 32px;
      text-align: center;
    }
    
    .title {
      font-size: 28px;
      font-weight: 700;
      margin-bottom: 8px;
      color: #4a5568; /* Darker gray for title */
    }
    
    .subtitle {
      font-size: 16px;
      color: #718096;
      margin-bottom: 24px;
    }
    
    .legend {
      display: flex;
      justify-content: center;
      gap: 24px;
      margin-bottom: 32px;
      flex-wrap: wrap;
    }
    
    .legend-item {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 14px;
      font-weight: 500;
      padding: 8px 16px;
      background: white;
      border-radius: 20px;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
      transition: transform 0.2s ease;
    }
    
    .legend-item:hover {
      transform: translateY(-2px);
    }
    
    .legend-color {
      width: 16px;
      height: 16px;
      border-radius: 50%;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    .grid-container {
      display: flex;
      flex-direction: column;
      gap: 12px;
      margin-bottom: 32px;
    }
    
    .grid-row {
      display: grid;
      grid-template-columns: repeat(${DEFAULT_COLS}, 1fr);
      gap: 12px;
    }
    
    .position-cell {
      min-height: 80px;
      border: 2px solid transparent;
      border-radius: 16px;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      padding: 16px;
      text-align: center;
      position: relative;
      overflow: hidden;
    }
    
    .position-cell::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
      opacity: 0;
      transition: opacity 0.3s ease;
    }
    
    .position-cell:hover::before {
      opacity: 1;
    }
    
    .position-cell.empty {
      border: none;
      cursor: default;
      background: transparent;
    }
    
    .position-cell.available {
      background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
      border-color: #e2e8f0;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }
    
    .position-cell.available:hover {
      background: linear-gradient(135deg, #edf2f7 0%, #e2e8f0 100%);
      border-color: #cbd5e0;
      transform: translateY(-2px);
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
    }
    
    .position-cell.selected {
      background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
      border-color: #38a169;
      color: white;
      box-shadow: 0 8px 24px rgba(72, 187, 120, 0.3);
      transform: translateY(-2px);
    }
    
    .position-cell.disabled {
      background: linear-gradient(135deg, #fc8181 0%, #e53e3e 100%);
      border-color: #e53e3e;
      color: white;
      cursor: not-allowed;
      opacity: 0.8;
      box-shadow: 0 4px 12px rgba(229, 62, 62, 0.2);
    }
    
    .position-content {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 4px;
    }
    
    .position-label {
      font-size: 13px;
      font-weight: 600;
      line-height: 1.2;
    }
    
    .selected-count {
      background: #4a5568; /* Solid dark gray */
      color: white;
      padding: 20px;
      border-radius: 16px;
      font-size: 16px;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
      text-align: center;
    }
    
    .selected-count strong {
      font-weight: 700;
      font-size: 18px;
    }
    
    .selected-list {
      margin-top: 12px;
      font-size: 14px;
      opacity: 0.9;
      line-height: 1.5;
    }
    
    @media (max-width: 768px) {
      .position-selector {
        padding: 16px;
      }
      
      .container {
        padding: 20px;
      }
      
      .title {
        font-size: 24px;
      }
      
      .legend {
        gap: 12px;
      }
      
      .position-cell {
        min-height: 60px;
        padding: 12px;
      }
      
      .position-label {
        font-size: 11px;
      }
    }
  `

  return (
    <div className="position-selector">
      <style>{styles}</style>

      <div className="container">
        <div className="header">
          <div className="title">Chart Position Selector</div>
          <div className="subtitle">Select positions where you want to place your charts</div>

          <div className="legend">
            <div className="legend-item">
              <div
                className="legend-color"
                style={{ background: "linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%)" }}
              ></div>
              <span>Available</span>
            </div>
            <div className="legend-item">
              <div
                className="legend-color"
                style={{ background: "linear-gradient(135deg, #48bb78 0%, #38a169 100%)" }}
              ></div>
              <span>Selected</span>
            </div>
            <div className="legend-item">
              <div
                className="legend-color"
                style={{ background: "linear-gradient(135deg, #fc8181 0%, #e53e3e 100%)" }}
              ></div>
              <span>Occupied/Unavailable</span>
            </div>
          </div>
        </div>

        <div className="grid-container">{renderGrid()}</div>

        <div className="selected-count">
          <strong>Selected Positions: {selectedPositions.size}</strong>
          <div className="selected-list">{Array.from(selectedPositions).join(" • ")}</div>
        </div>
      </div>
    </div>
  )
}

export default withStreamlitConnection(MyComponent)
