# UI/UX Design Guide

## 1. Design System Overview

The Hospital Management System uses a modern, clean design system built with Tailwind CSS and Bootstrap 5. The design prioritizes clarity, accessibility, and professional healthcare aesthetics.

## 2. Color Palette

### 2.1 Primary Colors

| Color Name | Hex Code | Usage |
|------------|----------|-------|
| Primary Blue | `#004ac6` | Primary buttons, links, active states |
| Primary Dark | `#003599` | Hover states, emphasis |
| Primary Light | `#e6f0ff` | Light backgrounds, badges |

### 2.2 Semantic Colors

| Color Name | Hex Code | Usage |
|------------|----------|-------|
| Success Green | `#2e7d32` | Success messages, confirmed status |
| Warning Amber | `#ed6c02` | Warnings, pending status |
| Error Red | `#d32f2f` | Errors, critical status, cancelled |
| Info Blue | `#0288d1` | Information, in-review status |
| Secondary Gray | `#6b7280` | Secondary text, muted elements |

### 2.3 Neutral Colors

| Color Name | Hex Code | Usage |
|------------|----------|-------|
| Surface | `#ffffff` | Card backgrounds, content areas |
| Surface Container | `#f8f9fa` | Container backgrounds |
| Surface Container Low | `#f2f4f6` | Hover states, active items |
| Outline Variant | `#e5e7eb` | Borders, dividers |
| On Surface | `#1f2937` | Primary text |
| On Surface Variant | `#6b7280` | Secondary text, labels |

## 3. Typography

### 3.1 Font Family

```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
```

### 3.2 Type Scale

| Class | Size | Weight | Line Height | Usage |
|-------|------|--------|-------------|-------|
| `font-headline-lg` | 2.25rem (36px) | 700 | 1.2 | Page titles |
| `font-headline-md` | 1.875rem (30px) | 700 | 1.3 | Section titles |
| `font-headline-sm` | 1.5rem (24px) | 600 | 1.4 | Card titles |
| `font-body-lg` | 1.125rem (18px) | 400 | 1.5 | Lead paragraphs |
| `font-body-md` | 1rem (16px) | 400 | 1.5 | Body text |
| `font-body-sm` | 0.875rem (14px) | 400 | 1.5 | Small text, captions |
| `font-label-md` | 0.9375rem (15px) | 500 | 1.4 | Button labels, inputs |
| `font-label-sm` | 0.8125rem (13px) | 500 | 1.4 | Badges, tags |

## 4. Component Styles

### 4.1 Sidebar

```css
/* Sidebar */
.sidebar {
    width: 256px;
    background: #ffffff;
    border-right: 1px solid #e5e7eb;
    position: fixed;
    height: 100vh;
    overflow-y: auto;
}

/* Sidebar Active State */
.sidebar-item.active {
    background-color: #f2f4f6;
    color: #004ac6;
    border-right: 4px solid #004ac6;
}

/* Sidebar Hover */
.sidebar-item:hover {
    background-color: #f2f4f6;
    color: #004ac6;
}
```

### 4.2 Navbar

```css
/* Top Navbar */
.navbar {
    height: 64px;
    background: #ffffff;
    border-bottom: 1px solid #e5e7eb;
    padding: 0 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

/* Notification Bell */
.nav-notification {
    position: relative;
    color: #6b7280;
}

.nav-notification .badge {
    position: absolute;
    top: -4px;
    right: -4px;
    background: #d32f2f;
    color: white;
    font-size: 10px;
    padding: 2px 5px;
    border-radius: 10px;
}
```

### 4.3 Cards

```css
/* Base Card */
.card {
    background: #ffffff;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    padding: 24px;
    margin-bottom: 16px;
}

/* Card Header */
.card-header {
    padding: 20px 24px;
    border-bottom: 1px solid #e5e7eb;
}

/* Card Body */
.card-body {
    padding: 24px;
}
```

### 4.4 Buttons

```css
/* Primary Button */
.btn-primary {
    background: #004ac6;
    color: white;
    padding: 10px 20px;
    border-radius: 8px;
    font-weight: 500;
    font-size: 15px;
    border: none;
    transition: all 0.2s;
}

.btn-primary:hover {
    background: #003599;
    transform: translateY(-1px);
}

/* Secondary Button */
.btn-secondary {
    background: #f2f4f6;
    color: #1f2937;
    padding: 10px 20px;
    border-radius: 8px;
    font-weight: 500;
    font-size: 15px;
    border: 1px solid #e5e7eb;
}

/* Danger Button */
.btn-danger {
    background: #d32f2f;
    color: white;
    padding: 10px 20px;
    border-radius: 8px;
    font-weight: 500;
    border: none;
}
```

### 4.5 Tables

```css
/* Table Container */
.table-container {
    background: #ffffff;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
    overflow: hidden;
}

/* Table */
table {
    width: 100%;
    border-collapse: collapse;
}

/* Table Header */
thead {
    background: #eceef0;
}

th {
    padding: 14px 20px;
    text-align: left;
    font-weight: 600;
    font-size: 13px;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Table Body */
td {
    padding: 16px 20px;
    border-bottom: 1px solid #e5e7eb;
    font-size: 14px;
    color: #1f2937;
}

/* Table Row Hover */
tbody tr:hover {
    background: #f2f4f6;
}
```

### 4.6 Badges

```css
/* Badge Base */
.badge {
    display: inline-flex;
    align-items: center;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 500;
    letter-spacing: 0.02em;
}

/* Badge Variants */
.badge-primary {
    background: #e6f0ff;
    color: #004ac6;
}

.badge-success {
    background: #e8f5e9;
    color: #2e7d32;
}

.badge-warning {
    background: #fff3e0;
    color: #ed6c02;
}

.badge-error {
    background: #ffebee;
    color: #d32f2f;
}

.badge-secondary {
    background: #f2f4f6;
    color: #6b7280;
}
```

### 4.7 Forms

```css
/* Form Input */
.form-input {
    width: 100%;
    padding: 12px 16px;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    font-size: 15px;
    color: #1f2937;
    background: #ffffff;
    transition: border-color 0.2s, box-shadow 0.2s;
}

.form-input:focus {
    outline: none;
    border-color: #004ac6;
    box-shadow: 0 0 0 3px rgba(0, 74, 198, 0.1);
}

/* Form Label */
.form-label {
    display: block;
    margin-bottom: 6px;
    font-size: 14px;
    font-weight: 500;
    color: #374151;
}

/* Form Error */
.form-error {
    color: #d32f2f;
    font-size: 13px;
    margin-top: 4px;
}
```

### 4.8 Alerts/Messages

```css
/* Alert Base */
.alert {
    padding: 16px 20px;
    border-radius: 8px;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 12px;
}

.alert-success {
    background: #e8f5e9;
    color: #2e7d32;
    border: 1px solid #c8e6c9;
}

.alert-error {
    background: #ffebee;
    color: #d32f2f;
    border: 1px solid #ffcdd2;
}

.alert-warning {
    background: #fff3e0;
    color: #ed6c02;
    border: 1px solid #ffe0b2;
}

.alert-info {
    background: #e3f2fd;
    color: #0288d1;
    border: 1px solid #bbdefb;
}
```

## 5. Spacing System

| Token | Value | Usage |
|-------|-------|-------|
| `spacing-xs` | 4px | Tight spacing within components |
| `spacing-sm` | 8px | Small gaps between elements |
| `spacing-md` | 16px | Standard component padding |
| `spacing-lg` | 24px | Section spacing |
| `spacing-xl` | 32px | Large section spacing |
| `spacing-2xl` | 48px | Page-level spacing |

### Spacing Classes (Tailwind)

```css
.p-xs { padding: 4px; }
.p-sm { padding: 8px; }
.p-md { padding: 16px; }
.p-lg { padding: 24px; }
.p-xl { padding: 32px; }

.m-xs { margin: 4px; }
.m-sm { margin: 8px; }
.m-md { margin: 16px; }
.m-lg { margin: 24px; }
.m-xl { margin: 32px; }
```

## 6. Module-Specific Pages

### 6.1 Authentication Pages
- Clean, centered login/register forms
- Minimal design with HMS branding
- Focus states with blue ring
- Error messages in red below inputs

### 6.2 Patient Dashboard
- Welcome banner with user name
- Upcoming appointments card
- Quick action buttons (Book Appointment, View Records)
- Recent activity feed
- Notification bell with unread count

### 6.3 Doctor Dashboard
- Today's appointments timeline
- Patient statistics cards
- Quick actions (Add Record, Create Prescription)
- Recent patients list with profile pictures
- Notification bell with unread count

### 6.4 Admin Dashboard
- Statistics cards (Patients, Doctors, Appointments, Revenue)
- Weekly appointment chart (bar graph)
- Recent activity table
- Department distribution pie chart
- Quick action buttons

### 6.5 Appointment Pages
- Calendar-style date picker
- Time slot grid selection
- Doctor cards with profile pictures and specialization
- Status badges with color coding
- Filter and search functionality

### 6.6 Medical Records
- Patient information header
- Diagnosis and treatment display
- Status indicators (Stable, Critical, etc.)
- Follow-up date reminders
- Doctor attribution with profile picture

### 6.7 Prescriptions
- Medicine list with dosage details
- Frequency and duration display
- Print-friendly layout
- Doctor signature section
- Automatic medicine reminder generation notice

### 6.8 Notifications
- Bell icon with live unread count
- Notification list with category icons
- Read/unread status indicators
- Action links to related pages
- Mark all as read functionality

## 7. Responsive Breakpoints

| Breakpoint | Width | Target Devices |
|------------|-------|----------------|
| sm | 640px | Large phones |
| md | 768px | Tablets |
| lg | 1024px | Laptops |
| xl | 1280px | Desktops |
| 2xl | 1536px | Large screens |

### Responsive Behavior
- Sidebar collapses to hamburger menu on mobile
- Tables scroll horizontally on small screens
- Cards stack vertically on mobile
- Forms use full width on mobile, constrained on desktop

## 8. Accessibility

- All interactive elements have focus states
- Color contrast meets WCAG AA standards
- Form inputs have associated labels
- Error messages are clearly associated with inputs
- Semantic HTML structure throughout
- Keyboard navigation supported

## 9. Animation and Transitions

| Element | Animation | Duration | Easing |
|---------|-----------|----------|--------|
| Buttons | Background color, transform | 200ms | ease-in-out |
| Cards | Box shadow on hover | 200ms | ease-out |
| Sidebar items | Background color | 150ms | ease-in-out |
| Notifications | Slide in from right | 300ms | ease-out |
| Modals | Fade in + scale | 250ms | ease-out |
