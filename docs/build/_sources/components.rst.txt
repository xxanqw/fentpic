UI Components
=============

FENTPIC includes a comprehensive component library documented with Storybook. This section describes the main UI components used throughout the application.

Storybook Setup
---------------

To view and interact with components:

1. **Install Node.js dependencies**::

    npm install

2. **Start Storybook**::

    npm run storybook

3. **Access Storybook**: Open http://localhost:6006

Component Library
-----------------

UploadCard Component
~~~~~~~~~~~~~~~~~~~~

A drag-and-drop upload card component for image uploads with preview functionality.

**Features:**

- Drag and drop file upload
- File format validation
- Size limit enforcement
- Preview functionality
- Multiple theme support
- Responsive design

**Properties:**

:theme: Visual theme ('light' or 'dark')
:maxFileSize: Maximum file size in MB (default: 20)
:acceptedFormats: Array of accepted file formats
:showPreview: Whether to show file preview (default: true)
:disabled: Disable upload functionality (default: false)

**Events:**

:onFileSelect: Triggered when files are selected
:onUpload: Triggered when upload starts

**Usage Example:**

.. code-block:: html

   <div class="upload-card">
     <!-- Component renders here -->
   </div>

**Variants:**

- **Default**: Dark theme with full functionality
- **Light Theme**: Light color scheme
- **Without Preview**: Simplified upload without preview
- **Disabled**: Non-interactive state

ImageCard Component
~~~~~~~~~~~~~~~~~~~

A card component for displaying uploaded images with metadata and action buttons.

**Features:**

- Image thumbnail display
- Metadata information (size, date, etc.)
- Privacy indicators (public/private)
- Action buttons (view, copy, delete)
- Multiple size variants
- Hover effects and animations

**Properties:**

:image: Image object with metadata
:theme: Visual theme ('light' or 'dark')
:showActions: Whether to show action buttons (default: true)
:showMetadata: Whether to show image metadata (default: true)
:size: Card size variant ('small', 'medium', 'large')

**Events:**

:onCopy: Triggered when copy button is clicked
:onDelete: Triggered when delete button is clicked
:onView: Triggered when view button is clicked

**Image Object Structure:**

.. code-block:: javascript

   {
     id: 1,
     filename: 'example.jpg',
     url: '/uploads/example.jpg',
     size: 1048576,
     uploaded_at: '2025-07-04T12:00:00Z',
     is_public: true
   }

**Variants:**

- **Default**: Medium card with full functionality
- **Light Theme**: Light color scheme
- **Private Image**: Shows private indicator
- **Small Size**: Compact card layout
- **Large Size**: Expanded card layout
- **Without Actions**: Display only, no interaction
- **Without Metadata**: Image and title only

Design System
-------------

Colors
~~~~~~

**Dark Theme:**

- Primary Background: ``#0f0f0f``
- Secondary Background: ``#1a1a1a``
- Surface Color: ``#262626``
- Text Primary: ``#ffffff``
- Text Secondary: ``#b3b3b3``
- Border Color: ``#404040``
- Accent Color: ``#3b82f6``

**Light Theme:**

- Primary Background: ``#ffffff``
- Secondary Background: ``#f8f9fa``
- Surface Color: ``#ffffff``
- Text Primary: ``#333333``
- Text Secondary: ``#666666``
- Border Color: ``#e0e0e0``
- Accent Color: ``#3b82f6``

Typography
~~~~~~~~~~

**Font Family:** Inter (Google Fonts)

**Font Weights:**

- Light: 300
- Regular: 400
- Medium: 500
- Semibold: 600
- Bold: 700

**Text Scales:**

- Heading 1: 2.5rem (40px)
- Heading 2: 2rem (32px)
- Heading 3: 1.75rem (28px)
- Heading 4: 1.5rem (24px)
- Body: 1rem (16px)
- Small: 0.875rem (14px)
- Caption: 0.75rem (12px)

Spacing
~~~~~~~

**Base Unit:** 4px

**Scale:**

- xs: 4px
- sm: 8px
- md: 16px
- lg: 24px
- xl: 32px
- 2xl: 48px
- 3xl: 64px

Border Radius
~~~~~~~~~~~~~

- Small: 4px
- Medium: 8px
- Large: 12px
- XLarge: 16px
- Full: 50%

Shadows
~~~~~~~

**Elevation Levels:**

- Level 1: ``0 2px 8px rgba(0, 0, 0, 0.1)``
- Level 2: ``0 4px 12px rgba(0, 0, 0, 0.15)``
- Level 3: ``0 8px 25px rgba(0, 0, 0, 0.15)``
- Level 4: ``0 16px 40px rgba(0, 0, 0, 0.2)``

Animations
~~~~~~~~~~

**Transitions:**

- Fast: 0.15s ease
- Normal: 0.3s ease
- Slow: 0.5s ease

**Common Animations:**

- Hover lift: ``transform: translateY(-2px)``
- Button press: ``transform: scale(0.98)``
- Fade in: ``opacity: 0 → 1``
- Slide up: ``transform: translateY(100%) → 0``

Component Guidelines
--------------------

Accessibility
~~~~~~~~~~~~~

All components follow WCAG 2.1 AA guidelines:

- **Keyboard Navigation**: Tab order and focus management
- **Screen Readers**: ARIA labels and semantic HTML
- **Color Contrast**: Minimum 4.5:1 ratio
- **Focus Indicators**: Visible focus states
- **Alternative Text**: Images have descriptive alt text

Responsive Design
~~~~~~~~~~~~~~~~~

Components are designed mobile-first:

- **Breakpoints**: 
  
  - Mobile: < 768px
  - Tablet: 768px - 1024px
  - Desktop: > 1024px

- **Flexible Layouts**: CSS Grid and Flexbox
- **Scalable Typography**: Relative units (rem, em)
- **Touch Targets**: Minimum 44px for interactive elements

Performance
~~~~~~~~~~~

- **Lazy Loading**: Images load on demand
- **CSS Animations**: Hardware-accelerated transforms
- **Bundle Size**: Minimal JavaScript footprint
- **Cache Strategy**: Aggressive caching for static assets

Testing
~~~~~~~

Components are tested for:

- **Visual Regression**: Automated screenshot comparison
- **Interaction Testing**: User event simulation
- **Accessibility Testing**: Automated a11y checks
- **Cross-browser**: Chrome, Firefox, Safari, Edge

Customization
-------------

Theme Variables
~~~~~~~~~~~~~~~

Components use CSS custom properties for theming:

.. code-block:: css

   :root {
     --bg-primary: #0f0f0f;
     --bg-secondary: #1a1a1a;
     --text-primary: #ffffff;
     --accent-color: #3b82f6;
     /* ... more variables */
   }

Custom Styling
~~~~~~~~~~~~~~

Override component styles:

.. code-block:: css

   .upload-card {
     --border-radius: 20px;
     --accent-color: #10b981;
   }

Contributing
------------

To add new components:

1. Create component in ``/static/components/``
2. Add Storybook story in ``/stories/``
3. Document in this guide
4. Add tests
5. Submit pull request

**Story Format:**

.. code-block:: javascript

   export default {
     title: 'Components/ComponentName',
     argTypes: {
       // Component properties
     }
   };

   export const Default = {
     render: (args) => createComponent(args),
     args: {
       // Default values
     }
   };

**Documentation Requirements:**

- Component description
- Property definitions
- Event descriptions
- Usage examples
- Accessibility notes
- Browser support
