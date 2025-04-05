import React from 'react';
import { Stage, Layer, Line } from 'react-konva';

interface ChartProps {
  planets: { [key: string]: any };
  ascendant: { longitude: number; sign: string };
  houses: number[];
  navamsa?: { [key: string]: { navamsa_sign: string; navamsa_sign_index: number } };
}

const NorthIndianChart: React.FC<ChartProps> = () => {
  // Chart dimensions
  const width = 300;
  const height = 300;
  const centerX = width / 2;
  const centerY = height / 2;
  const outerRadius = 150;
  const innerRadius = 75;

  // Outer diamond points (top, right, bottom, left)
  const outerPoints = [
    centerX, centerY - outerRadius,
    centerX + outerRadius, centerY,
    centerX, centerY + outerRadius,
    centerX - outerRadius, centerY,
    centerX, centerY - outerRadius,
  ];

  return (
    <Stage width={width} height={height}>
      <Layer>
        {/* Outer Diamond */}
        <Line
          points={outerPoints}
          stroke="black"
          strokeWidth={2}
          closed
        />
        <Line points={[0, 0, width, height]} stroke="black" strokeWidth={2} />
        <Line points={[0, height, width, 0]} stroke="black" strokeWidth={2} />
        <Line points={[0, 0, 0, height]} stroke="black" strokeWidth={4} />
        <Line points={[0, 0, width, 0]} stroke="black" strokeWidth={4} />
        <Line points={[0, height, width, height]} stroke="black" strokeWidth={4} />
        <Line points={[width, 0, width, height]} stroke="black" strokeWidth={4} />
      </Layer>
    </Stage>
  );
};

export default NorthIndianChart;