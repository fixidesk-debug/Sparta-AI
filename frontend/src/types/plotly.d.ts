/**
 * Type declarations for plotly modules
 */

declare module 'react-plotly.js' {
  import { Component } from 'react';
  import * as Plotly from 'plotly.js';

  export interface PlotParams {
    data: Plotly.Data[];
    layout?: Partial<Plotly.Layout>;
    config?: Partial<Plotly.Config>;
    frames?: Plotly.Frame[];
    onInitialized?: (figure: Readonly<PlotParams>, graphDiv: HTMLElement) => void;
    onUpdate?: (figure: Readonly<PlotParams>, graphDiv: HTMLElement) => void;
    onPurge?: (figure: Readonly<PlotParams>, graphDiv: HTMLElement) => void;
    onError?: (err: any) => void;
    divId?: string;
    className?: string;
    style?: React.CSSProperties;
    useResizeHandler?: boolean;
    debug?: boolean;
    onAfterExport?: () => void;
    onAfterPlot?: () => void;
    onAnimated?: () => void;
    onAnimatingFrame?: (event: any) => void;
    onAnimationInterrupted?: () => void;
    onAutoSize?: () => void;
    onBeforeExport?: () => void;
    onButtonClicked?: (event: any) => void;
    onClick?: (event: any) => void;
    onClickAnnotation?: (event: any) => void;
    onDeselect?: () => void;
    onDoubleClick?: () => void;
    onFramework?: () => void;
    onHover?: (event: any) => void;
    onLegendClick?: (event: any) => boolean;
    onLegendDoubleClick?: (event: any) => boolean;
    onRelayout?: (event: any) => void;
    onRestyle?: (event: any) => void;
    onRedraw?: () => void;
    onSelected?: (event: any) => void;
    onSelecting?: (event: any) => void;
    onSliderChange?: (event: any) => void;
    onSliderEnd?: (event: any) => void;
    onSliderStart?: (event: any) => void;
    onSunburstClick?: (event: any) => void;
    onTransitioning?: () => void;
    onTransitionInterrupted?: () => void;
    onUnhover?: (event: any) => void;
    onWebGlContextLost?: () => void;
  }

  export default class Plot extends Component<PlotParams> {}
}

declare module 'plotly.js' {
  export interface Data {
    x?: any[];
    y?: any[];
    z?: any[];
    type?: string;
    mode?: string;
    name?: string;
    marker?: any;
    line?: any;
    text?: string | string[];
    hoverinfo?: string;
    [key: string]: any;
  }

  export interface Layout {
    title?: string | { text: string; [key: string]: any };
    xaxis?: any;
    yaxis?: any;
    width?: number;
    height?: number;
    showlegend?: boolean;
    margin?: { l?: number; r?: number; t?: number; b?: number };
    [key: string]: any;
  }

  export interface Config {
    displayModeBar?: boolean;
    responsive?: boolean;
    [key: string]: any;
  }

  export interface Frame {
    name: string;
    data?: Data[];
    layout?: Partial<Layout>;
    [key: string]: any;
  }
}
