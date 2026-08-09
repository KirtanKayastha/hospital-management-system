# UI Design Guide — Hospital Management System

## 1. Color Palette

| Token | Hex | Usage |
|-------|-----|-------|
| Primary | `#004ac6` | Primary actions, links, active states |
| Primary Container | `#2563eb` | Elevated primary surfaces, button backgrounds |
| Surface | `#f7f9fb` | Page background, app shell |
| Surface Container | `#ffffff` | Cards, modals, raised panels |
| On Surface | `#191c1e` | Primary text, headings |
| On Surface Variant | `#434655` | Secondary text, captions |
| Outline Variant | `#c3c6d7` | Borders, dividers, input strokes |
| Error | `#ba1a1a` | Error messages, destructive actions |
| Error Container | `#ffdad6` | Error notification backgrounds |
| Secondary | `#006c49` | Success states, positive actions |
| Secondary Container | `#6cf8bb` | Success badges, confirmation highlights |
| Tertiary | `#784b00` | Warnings, caution indicators |
| Tertiary Container | `#996100` | Warning surfaces, alert banners |

---

## 2. Typography

**Font Family:** Inter

| Element | Size | Weight | Line Height | Usage |
|---------|------|--------|-------------|-------|
| Page Title | 24–28px | 700 | 1.2 | Dashboard headers, module titles |
| Section Heading | 18–20px | 600 | 1.3 | Card titles, form section labels |
| Body Text | 14–16px | 400 | 1.5 | Paragraphs, table content, descriptions |
| Label | 12–14px | 500 | 1.4 | Input labels, button text, captions |

**Rules:**
- Use `700` weight only for top-level page titles.
- Use `600` weight for section headings and card headers.
- Use `500` weight for labels, button text, and nav items.
- Use `400` weight for all body and table content.
- Maintain minimum 1.4 line-height for readability.

---

## 3. Component Styles

### 3.1 Sidebar
- **Width:** 256px
- **Background:** Surface Container (`#ffffff`)
- **Active State:** Blue left border (Primary `#004ac6`)
- **Hover:** Light surface tint
- **Padding:** 16px vertical, 24px horizontal
- **Logo area:** 64px height, border-bottom

### 3.2 Navbar
- **Height:** 64px
- **Background:** Surface Container (`#ffffff`)
- **Border:** Bottom, Outline Variant (`#c3c6d7`)
- **Content:** Search, notifications, user avatar, breadcrumbs
- **Z-index:** Above sidebar and page content

### 3.3 Cards
- **Background:** Surface Container (`#ffffff`)
- **Border Radius:** 12px
- **Shadow:** `0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06)`
- **Padding:** 24px
- **Margin:** 16px gap between cards
- **Hover:** Subtle elevation increase (optional)

### 3.4 Buttons
- **Border Radius:** 8px (rounded)
- **Primary Button:** Background Primary Container (`#2563eb`), text white
- **Secondary Button:** Outline style, border Outline Variant, text On Surface
- **Destructive Button:** Background Error (`#ba1a1a`), text white
- **Padding:** 8px 16px vertical/horizontal
- **Font Weight:** 500
- **Font Size:** 14px
- **States:** Hover darken 8%, Active darken 12%, Disabled opacity 40%

### 3.5 Tables
- **Header Background:** `#eceef0`
- **Header Text:** On Surface (`#191c1e`), weight 600
- **Row Height:** 48px minimum
- **Row Hover:** `#f2f4f6`
- **Border:** Bottom row separator, Outline Variant (`#c3c6d7`)
- **Font Size:** 14px
- **Padding:** 12px 16px

### 3.6 Badges
- **Shape:** `rounded-full`
- **Padding:** 4px 12px
- **Font Size:** 12px
- **Font Weight:** 500
- **Border Radius:** 9999px

### 3.7 Forms
- **Input Height:** 40px
- **Border Radius:** 8px
- **Border:** 1px solid Outline Variant (`#c3c6d7`)
- **Focus Ring:** 2px solid Primary (`#004ac6`), offset 2px
- **Label Position:** Above input, Label style (12–14px, 500 weight)
- **Error State:** Border Error (`#ba1a1a`), helper text in Error
- **Background:** Surface Container (`#ffffff`)

---

## 4. Spacing System

| Token | Value | Usage |
|-------|-------|-------|
| xs | 4px | Icon padding, tight gaps |
| sm | 8px | Between related items, input internal spacing |
| md | 16px | Card padding vertical, list gaps |
| lg | 24px | Card padding horizontal, section spacing |
| xl | 32px | Between major sections, page margins |
| xxl | 48px | Between distinct page areas, large containers |

**Rules:**
- Use multiples of the base spacing scale (4px).
- Horizontal padding typically uses lg (24px) for cards.
- Vertical spacing between sections uses xl (32px).
- Page-level margins use xxl (48px) on desktop, xl (32px) on tablet.

---

## 5. Module-Specific Pages

### 5.1 Patient Module
- Patient Dashboard
- Patient Registration / Onboarding
- Appointment Booking
- Appointment History
- Medical Records View
- Prescriptions View
- Billing & Invoices
- Profile Settings

### 5.2 Doctor Module
- Doctor Dashboard
- Appointment Schedule (Calendar)
- Patient List
- Medical Records (Write / Edit)
- Prescriptions (Create / View)
- Lab Reports Review
- Profile Settings

### 5.3 Admin Module
- Admin Dashboard
- User Management (Doctors / Patients / Staff)
- Department Management
- Appointment Management
- Billing & Finance Overview
- Reports & Analytics
- System Settings
- Profile Settings

### 5.4 Public Module
- Landing Page
- About Us
- Departments Overview
- Doctors Directory
- Contact Us
- FAQ
- Emergency Contact

---

## 6. Badge Status Reference

| Status | Background | Text Color | Usage |
|--------|-----------|------------|-------|
| Scheduled | `#dbeafe` | `#1e40af` | Upcoming appointments |
| Confirmed | `#d1fae5` | `#065f46` | Confirmed bookings |
| Completed | `#d1fae5` | `#065f46` | Finished appointments |
| Cancelled | `#fee2e2` | `#991b1b` | Cancelled by user or staff |
| In Progress | `#fef3c7` | `#92400e` | Active consultations |
| Pending | `#f3f4f6` | `#374151` | Awaiting approval |
| Paid | `#d1fae5` | `#065f46` | Successful payments |
| Unpaid | `#fee2e2` | `#991b1b` | Outstanding payments |
| Admitted | `#ede9fe` | `#5b21b6` | Inpatient status |
| Discharged | `#d1fae5` | `#065f46` | Released from care |

---

## 7. Implementation Checklist

Use this checklist when building or reviewing any page in the Hospital Management System.

### General
- [ ] Page background uses Surface (`#f7f9fb`)
- [ ] All cards use Surface Container (`#ffffff`) with 12px radius and 24px padding
- [ ] Typography follows scale: Page Title (24–28px, 700), Section Heading (18–20px, 600), Body (14–16px, 400), Label (12–14px, 500)
- [ ] Font family is Inter throughout
- [ ] Spacing follows 4px scale (xs/sm/md/lg/xl/xxl)
- [ ] No custom colors outside defined palette

### Layout
- [ ] Sidebar width 256px, white bg, active state blue left border
- [ ] Navbar height 64px, white bg, bottom border Outline Variant
- [ ] Page content has consistent xxl (48px) outer padding
- [ ] Responsive breakpoints handled (desktop/tablet/mobile)

### Interactive Elements
- [ ] Buttons use rounded style (8px radius)
- [ ] Primary buttons use Primary Container background with white text
- [ ] Hover states darken background 8%
- [ ] Active states darken background 12%
- [ ] Disabled states show 40% opacity
- [ ] Focus rings use 2px solid Primary with 2px offset

### Tables
- [ ] Header background `#eceef0`
- [ ] Row hover `#f2f4f6`
- [ ] Row height minimum 48px
- [ ] Font size 14px, weight 400 for rows
- [ ] Border-bottom separators use Outline Variant

### Forms
- [ ] Input height 40px, border-radius 8px
- [ ] Border color Outline Variant by default
- [ ] Focus ring 2px solid Primary, 2px offset
- [ ] Error state uses Error border and Error text
- [ ] Labels positioned above inputs

### Badges
- [ ] All badges use `rounded-full`
- [ ] Padding 4px 12px
- [ ] Font size 12px, weight 500
- [ ] Status colors match Badge Status Reference table

### Accessibility
- [ ] Color contrast ratio meets WCAG AA (4.5:1 for text)
- [ ] Interactive elements have visible focus indicators
- [ ] Form inputs have associated labels
- [ ] Error messages are descriptive and visible
