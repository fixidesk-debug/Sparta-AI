import React from 'react';

type IconProps = {
  size?: number;
  className?: string;
  strokeWidth?: number;
  ariaHidden?: boolean;
};

const mk = (path: string) => ({ size = 16, className, strokeWidth = 1.5 }: IconProps) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth={strokeWidth}
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
    aria-hidden="true"
    focusable="false"
  >
    <path d={path} />
  </svg>
);

// Minimal icon approximations (keeps bundle local so project compiles without external lib)
export const Upload = mk('M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4');
export const File = mk('M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z');
export const Folder = mk('M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5');
export const FileText = mk('M14 2v6h6');
export const Image = mk('M21 15l-5-5L9 21H3V3h18z');
export const Archive = mk('M3 7h18M21 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7');
export const Grid = mk('M3 3h8v8H3z M13 3h8v8h-8z M3 13h8v8H3z M13 13h8v8h-8z');
export const List = mk('M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01');
export const Search = mk('M21 21l-6-6');
export const X = mk('M18 6L6 18M6 6l12 12');
export const Check = mk('M20 6L9 17l-5-5');
export const AlertCircle = mk('M12 9v4M12 17h.01');
export const Download = mk('M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4');
export const Trash2 = mk('M3 6h18M8 6v12M16 6v12M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6');
export const MoreVertical = mk('M12 6v.01M12 12v.01M12 18v.01');
export const RefreshCw = mk('M21 12a9 9 0 1 0-3 6');

// Additional placeholder icons used across the app
export const Eye = mk('M1 12s4-8 11-8 11 8 11 8-4 8-11 8S1 12 1 12z M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6z');
export const Users = mk('M17 21v-2a4 4 0 0 0-3-3.87 M7 21v-2a4 4 0 0 1 3-3.87');
export const Mail = mk('M4 4h16v12H4z M4 4l8 8 8-8');
export const Facebook = mk('M18 2h-3a4 4 0 0 0-4 4v3H8v4h3v8h4v-8h2.5l.5-4H15V6a1 1 0 0 1 1-1h2z');
export const Twitter = mk('M23 3a10.9 10.9 0 0 1-3.14 1.53A4.48 4.48 0 0 0 12 7.77v1A10.66 10.66 0 0 1 3 4s-4 9 5 13a11.64 11.64 0 0 1-7 2c9 5 20 0 20-11.5a4.5 4.5 0 0 0-.08-.83A7.72 7.72 0 0 0 23 3z');
export const Linkedin = mk('M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-14h4v2');
export const MessageCircle = mk('M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7A8.38 8.38 0 0 1 4 11.5 8.5 8.5 0 0 1 12.5 3 8.38 8.38 0 0 1 21 11.5z');
export const QrCode = mk('M3 3h8v8H3z M13 3h8v8h-8z M3 13h8v8H3z M13 13h2v2h-2z M17 17h2v2h-2z');
export const Lock = mk('M3 11V9a5 5 0 0 1 10 0v2 M5 11h6v8H5z');
export const Edit = mk('M3 21v-3.87L14.12 6.01l3.87 3.87L6.87 21H3z');
export const Shield = mk('M12 2l7 4v6c0 5-3.58 9.74-7 11-3.42-1.26-7-6-7-11V6l7-4z');
export const Calendar = mk('M3 8h18M16 2v4M8 2v4M3 12h18v8H3z');
export const Copy = mk('M16 1H4a2 2 0 0 0-2 2v12h2V3h12V1z M21 7H8a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h13a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2z');
export const Send = mk('M22 2L11 13');
export const Paperclip = mk('M21 12v6a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4V8a4 4 0 0 1 4-4h6');
export const Mic = mk('M12 1v11M8 5v3a4 4 0 0 0 8 0V5');
export const Smile = mk('M8 14s1.5 2 4 2 4-2 4-2');
export const ChevronLeft = mk('M15 18l-6-6 6-6');
export const ChevronRight = mk('M9 6l6 6-6 6');
export const Maximize2 = mk('M8 3v3h3');

// Settings and configuration icons
export const Settings = mk('M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20z M12 6v6l4 2');
export const Palette = mk('M12 2a10 10 0 1 0 0 20c1.1 0 2-.9 2-2v-1a2 2 0 0 0-2-2H9a1 1 0 0 1 0-2h3c1.1 0 2-.9 2-2s-.9-2-2-2a10 10 0 0 0 0 0z');
export const Zap = mk('M13 2L3 14h8l-1 8 10-12h-8l1-8z');
export const Database = mk('M3 5c0-1.5 4-3 9-3s9 1.5 9 3v14c0 1.5-4 3-9 3s-9-1.5-9-3V5z M3 9c0 1.5 4 3 9 3s9-1.5 9-3');
export const Code = mk('M16 18l6-6-6-6 M8 6l-6 6 6 6');
export const HelpCircle = mk('M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20z M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3 M12 17h.01');
export const Save = mk('M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z M7 3v5h8 M17 21v-8H7v8');
export const RotateCcw = mk('M1 4v6h6 M3.51 15a9 9 0 1 0 2.13-9.36L1 10');
export const Moon = mk('M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z');
export const Sun = mk('M12 1v2 M12 21v2 M4.22 4.22l1.42 1.42 M18.36 18.36l1.42 1.42 M1 12h2 M21 12h2 M4.22 19.78l1.42-1.42 M18.36 5.64l1.42-1.42');
export const Monitor = mk('M20 3H4a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V5a2 2 0 0 0-2-2z M8 21h8 M12 17v4');
export const Bell = mk('M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9 M13.73 21a2 2 0 0 1-3.46 0');
export const Globe = mk('M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20z M2 12h20 M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z');
export const Sliders = mk('M4 21v-7 M4 10V3 M12 21v-9 M12 8V3 M20 21v-5 M20 12V3 M1 14h6 M9 8h6 M17 16h6');
export const CheckCircle = mk('M22 11.08V12a10 10 0 1 1-5.93-9.14 M22 4L12 14.01l-3-3');
export const XCircle = mk('M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20z M15 9l-6 6 M9 9l6 6');
export const ChevronDown = mk('M6 9l6 6 6-6');
export const Menu = mk('M3 12h18 M3 6h18 M3 18h18');
export const EyeOff = mk('M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94 M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19 M1 1l22 22 M8.88 8.88a3 3 0 1 0 4.24 4.24');

// Performance and monitoring icons
export const Activity = mk('M22 12h-4l-3 9L9 3l-3 9H2');
export const TrendingUp = mk('M23 6l-9.5 9.5-5-5L1 18');
export const TrendingDown = mk('M23 18L13.5 8.5l-5 5L1 6');
export const AlertTriangle = mk('M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z M12 9v4 M12 17h.01');
export const BarChart2 = mk('M18 20V10 M12 20V4 M6 20v-6');
export const PieChart = mk('M21.21 15.89A10 10 0 1 1 8 2.83 M22 12A10 10 0 0 0 12 2v10z');
export const Clock = mk('M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20z M12 6v6l4 2');
export const Cpu = mk('M4 4h16v16H4z M9 9h6v6H9z M9 1v3 M15 1v3 M9 20v3 M15 20v3 M20 9h3 M20 14h3 M1 9h3 M1 15h3');
export const HardDrive = mk('M22 12H2 M5.45 5.11L2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z M6 16h.01 M10 16h.01');
export const Wifi = mk('M5 12.55a11 11 0 0 1 14.08 0 M1.42 9a16 16 0 0 1 21.16 0 M8.53 16.11a6 6 0 0 1 6.95 0 M12 20h.01');

export default {};
