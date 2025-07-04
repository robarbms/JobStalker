import React from 'react';
import { Tooltip, Legend, PieChart, Pie, Cell, Label } from 'recharts';

export const hslToHex = ({hue: h, saturation: s, lightness: l}: {hue: number, saturation: number, lightness: number}): string => {
  h /= 360;
  s /= 100;
  l /= 100;
  let r, g, b;
  if (s === 0) {
    r = g = b = l; // achromatic
  } else {
    const hue2rgb = (p: number, q: number, t: number) => {
      if (t < 0) t += 1;
      if (t > 1) t -= 1;
      if (t < 1 / 6) return p + (q - p) * 6 * t;
      if (t < 1 / 2) return q;
      if (t < 2 / 3) return p + (q - p) * (2 / 3 - t) * 6;
      return p;
    };
    const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
    const p = 2 * l - q;
    r = hue2rgb(p, q, h + 1 / 3);
    g = hue2rgb(p, q, h);
    b = hue2rgb(p, q, h - 1 / 3);
  }
  const toHex = (x: number) => {
    const hex = Math.round(x * 255).toString(16);
    return hex.length === 1 ? "0" + hex : hex;
  };
  return `#${toHex(r)}${toHex(g)}${toHex(b)}`;
}

type TagCategoryChartProps = {
    data: any;
    tagColors: {[tag: string]: any};
}

const TagCategoryChart = (props: TagCategoryChartProps) => {
    const { data, tagColors } = props;
    const { children, total } = data;
    const tagData: {
        name: string,
        value: number
    }[] = children.map(((tag: any) => ({
        name: tag.name,
        value: tag.count
    })));

    return (
        <PieChart 
            width={620}
            height={300}
            data={data}
            margin={{top: 5, right: 30, left: 20, bottom: 5}}>
            <Legend layout="vertical" verticalAlign="middle" align="left" />
            <Tooltip />
            <Pie data={tagData} dataKey="value" label innerRadius={80} paddingAngle={1}>
                {tagData.map((tag, index) => <Cell key={index} fill={hslToHex(tagColors[tag.name as string]) || "#8884d8"} />)}
                <Label position="center" value={`Total tags: ${total}`} />
            </Pie>
        </PieChart>
    );
}

/**
 * Properties for the Keyword group overview component
 */
type KeywordGroupOverviewProps = {
    data: any;
    tagColors: {[tag: string]: any};
}

/**
 * A component that shows data about a group of tags
 * @param props data: data used to render charts and tag filters
 * @returns 
 */
const KeywordGroupOverview = (props: KeywordGroupOverviewProps) => {
    const { data, tagColors } = props;

    return (
        <div className="keyword-group-overview">
            <TagCategoryChart data={data} tagColors={tagColors} />
        </div>
    )
}

export default KeywordGroupOverview;
