"use client"

import { Streamlit, withStreamlitConnection, type ComponentProps } from "streamlit-component-lib"
import { useCallback, useEffect, useState, type ReactElement } from "react"

interface ColorOption {
  name: string
  color: string | string[] // hex para solid, array de hex para gradient
}

function MyComponent({ args, disabled, theme }: ComponentProps): ReactElement {
  const { colors = [] } = args

  // Parse colors from the input format
  const colorOptions: ColorOption[] = colors.map((colorObj: any) => {
    const { name, color } = colorObj
    
    // Check if it's a gradient (array of colors)
    if (Array.isArray(color)) {
      console.log('Found gradient:', name, color)
      return {
        name,
        color: color as string[]
      }
    } else {
      // Solid color
      console.log('Found solid color:', name, color)
      return {
        name,
        color: color as string
      }
    }
  })

  // State to manage selected color
  const [selectedColor, setSelectedColor] = useState<ColorOption | null>(null)

  // Send selected color back to Streamlit
  useEffect(() => {
    Streamlit.setComponentValue(selectedColor)
  }, [selectedColor])

  // Set frame height
  useEffect(() => {
    Streamlit.setFrameHeight(80)
  }, [])

  // Handle color selection
  const handleColorClick = useCallback((colorOption: ColorOption) => {
    setSelectedColor(prevColor => 
      prevColor && prevColor.name === colorOption.name ? null : colorOption
    )
  }, [])

  // Generate gradient style
  const getGradientStyle = (colors: string[]) => {
    const gradientColors = colors.join(', ')
    console.log('Gradient style:', `linear-gradient(135deg, ${gradientColors})`)
    return {
      background: `linear-gradient(135deg, ${gradientColors})`,
      backgroundSize: '100% 100%'
    }
  }

  const styles = `
    .color-selector {
      padding: 8px;
      background: transparent;
    }
    
    .colors-grid {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      justify-content: center;
    }
    
    .color-option {
      cursor: pointer;
      transition: all 0.2s ease;
      border-radius: 50%;
      border: 2px solid transparent;
    }
    
    .color-option:hover {
      transform: scale(1.1);
    }
    
    .color-option.selected {
      border-color: #3b82f6;
      transform: scale(1.15);
    }
    
    .color-circle {
      width: 24px;
      height: 24px;
      border-radius: 50%;
      border: 2px solid #ffffff;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
      transition: all 0.2s ease;
      position: relative;
    }
    
    .color-option.selected .color-circle::after {
      content: '✓';
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      color: white;
      font-size: 10px;
      font-weight: bold;
      text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
    }
    
    @media (max-width: 480px) {
      .color-circle {
        width: 20px;
        height: 20px;
      }
    }
  `

  return (
    <div className="color-selector">
      <style>{styles}</style>

      {colorOptions.length > 0 ? (
        <div className="colors-grid">
          {colorOptions.map((color) => (
            <div
              key={color.name}
              className={`color-option ${selectedColor && selectedColor.name === color.name ? 'selected' : ''}`}
              onClick={() => handleColorClick(color)}
            >
              <div
                className="color-circle"
                style={Array.isArray(color.color) 
                  ? getGradientStyle(color.color)
                  : { backgroundColor: color.color }
                }
                title={`${color.name}: ${Array.isArray(color.color) 
                  ? `gradient(${color.color.join(', ')})`
                  : color.color
                }`}
              />
            </div>
          ))}
        </div>
      ) : null}
    </div>
  )
}

export default withStreamlitConnection(MyComponent) 