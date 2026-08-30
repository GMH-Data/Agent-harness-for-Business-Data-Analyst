---
name: Luminous Enterprise
colors:
  surface: '#f9f9ff'
  surface-dim: '#d7d9e6'
  surface-bright: '#f9f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f1f3ff'
  surface-container: '#ebedfa'
  surface-container-high: '#e5e8f4'
  surface-container-highest: '#e0e2ee'
  on-surface: '#181c24'
  on-surface-variant: '#584237'
  inverse-surface: '#2d3039'
  inverse-on-surface: '#eef0fc'
  outline: '#8c7164'
  outline-variant: '#e0c0b1'
  surface-tint: '#9d4300'
  primary: '#9d4300'
  on-primary: '#ffffff'
  primary-container: '#f97316'
  on-primary-container: '#582200'
  inverse-primary: '#ffb690'
  secondary: '#555f6f'
  on-secondary: '#ffffff'
  secondary-container: '#d6e0f3'
  on-secondary-container: '#596373'
  tertiary: '#006398'
  on-tertiary: '#ffffff'
  tertiary-container: '#00a2f4'
  on-tertiary-container: '#003554'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffdbca'
  primary-fixed-dim: '#ffb690'
  on-primary-fixed: '#341100'
  on-primary-fixed-variant: '#783200'
  secondary-fixed: '#d9e3f6'
  secondary-fixed-dim: '#bdc7d9'
  on-secondary-fixed: '#121c2a'
  on-secondary-fixed-variant: '#3d4756'
  tertiary-fixed: '#cde5ff'
  tertiary-fixed-dim: '#93ccff'
  on-tertiary-fixed: '#001d32'
  on-tertiary-fixed-variant: '#004b74'
  background: '#f9f9ff'
  on-background: '#181c24'
  surface-variant: '#e0e2ee'
typography:
  display-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 48px
    fontWeight: '700'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '700'
    lineHeight: '1.2'
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.3'
  body-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.6'
  label-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 14px
    fontWeight: '600'
    lineHeight: '1.4'
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 12px
    fontWeight: '500'
    lineHeight: '1.4'
  headline-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 28px
    fontWeight: '700'
    lineHeight: '1.2'
rounded:
  sm: 0.5rem
  DEFAULT: 1rem
  md: 1.5rem
  lg: 2rem
  xl: 3rem
  full: 9999px
spacing:
  page-margin: 2.5rem
  section-gap: 2rem
  card-padding: 1.5rem
  gutter: 1rem
  stack-sm: 0.5rem
  stack-md: 1rem
---

## Brand & Style

The design system is built for a high-performance enterprise AI environment that prioritizes clarity, depth, and a sense of intellectual space. The aesthetic is rooted in **Glassmorphism**, utilizing translucent layers to create a multi-dimensional workspace that feels lighter than traditional enterprise software. 

By blending organic background tones with crisp, frosted-glass interfaces, the UI achieves a sophisticated balance between technical power and human-centric warmth. The target experience is one of "focused transparency"—where the complexity of AI is housed within an interface that feels breathable and premium.

## Colors

The palette is anchored by a warm, organic base (`#eaddd7`) which serves as the canvas for the glass effects. 

- **Primary Accent**: Orange (`#f97316`) is used sparingly for critical actions, status indicators, and data highlights to provide energy against the neutral backdrop.
- **Surface Strategy**: This design system relies on alpha-blended whites to create depth. Use `bg-glass` for navigation sidebars and secondary panels, while `bg-glass-card` provides higher legibility for data-heavy content. `bg-glass-dark` is reserved for high-contrast overlays or specific tooltips where focus is paramount.
- **Text**: Deep slate (`#1f2937`) ensures AAA accessibility on all glass surfaces, while muted slate (`#8b8e99`) handles secondary metadata and placeholder states.

## Typography

The design system utilizes **Plus Jakarta Sans** across all levels to maintain a modern, friendly, yet professional tone. The typeface's open counters and geometric structure ensure excellent legibility even when placed over semi-transparent glass backgrounds.

For enterprise dashboards, typography should emphasize hierarchy through weight rather than just size. Use `label-md` in semi-bold for table headers and UI controls. Display and Headline styles should utilize slight negative letter spacing to maintain a tight, "designed" feel on large monitor setups.

## Layout & Spacing

The layout follows a **fluid grid philosophy** with generous breathing room to offset the density of AI data. 

- **Outer Margins**: A standard `p-10` (2.5rem) margin is applied to the primary viewport to frame the content.
- **The Floating Grid**: Components should not touch the edges of the screen. Instead, they "float" over the base background with consistent `section-gap` spacing.
- **Mobile Adaptation**: On smaller screens, page margins reduce to 1rem, and the multi-column dashboard reflows into a single-column vertical stack. The glass panels lose their outer margins to maximize horizontal real estate.

## Elevation & Depth

Depth is achieved through the intersection of transparency, blur, and subtle borders rather than heavy shadows.

- **Backdrop Filter**: All glass elements must apply a `blur(12px)` to the underlying layers to maintain text legibility.
- **Glass Borders**: To define edges, use a 1px solid border with `rgba(255, 255, 255, 0.4)`. This creates a "specular highlight" effect that makes the panels pop from the background.
- **Z-Axis Hierarchy**:
    1. **Level 0 (Base)**: The `#eaddd7` canvas.
    2. **Level 1 (Panels)**: `bg-glass` used for navigation and sidebars.
    3. **Level 2 (Cards)**: `bg-glass-card` for primary interactive elements and data widgets.
    4. **Level 3 (Pop-overs)**: `bg-glass-dark` or standard glass with a soft `0 20px 40px rgba(0,0,0,0.1)` shadow for modals and menus.

## Shapes

The design system employs an ultra-rounded shape language to soften the "industrial" feel of enterprise data.

- **Primary Containers**: Large dashboard sections and the main app container use a `40px` (`rounded-[40px]`) corner radius.
- **UI Components**: Cards, buttons, and input groups use a `30px` (`rounded-3xl`) radius.
- **Small Elements**: Chips, tags, and checkboxes should remain fully rounded (pill-shaped) to maintain consistency with the overarching soft-geometric theme.

## Components

- **Buttons**: Primary buttons use the Accent Orange (`#f97316`) with white text. Secondary buttons should be "Ghost Glass"—transparent with a white 1px border and 12px backdrop blur.
- **Cards**: Use the `bg-glass-card` surface. Cards must include a `p-6` internal padding. Titles within cards use `headline-md`.
- **Input Fields**: Inputs should be rendered as semi-transparent wells (`rgba(255,255,255,0.3)`) with a `rounded-3xl` shape. On focus, the border transitions to the primary orange.
- **Chips/Badges**: Small pill-shaped containers with `bg-glass-dark` and white text for status, or light glass with orange text for active filters.
- **Lists**: Tables and lists should remove row borders in favor of "hover-glass" states, where a row highlights with increased opacity when the user interacts with it.
- **AI Specifics**: For AI chat or streaming data, use a distinct `bg-glass-dark` bubble to differentiate machine-generated content from the system UI.