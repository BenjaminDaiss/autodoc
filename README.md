# AutoDoc - Offline PDF Generator

Generate professional PDFs from templates that automatically adjust to variable-length content. Works completely offline in the browser!

## Features

- **✅ Fully Offline**: No server required, runs entirely in your browser
- **📏 Variable Content**: Text fields automatically resize - no fixed gaps or form fields
- **🎨 Template-Based**: Easy to customize layout in `src/pdfTemplate.js`
- **⚡ Real-time Preview**: See changes as you type
- **📱 Responsive**: Works on desktop and mobile

## How It Works

The app uses **pdfmake** to generate PDFs programmatically from templates. Unlike traditional PDF form filling (which requires fixed-size fields), this approach:

1. Takes your data (name, address, notes, etc.)
2. Runs it through a template in [src/pdfTemplate.js](src/pdfTemplate.js)
3. Generates a complete PDF with proper layout and flow
4. Content automatically adjusts - add 2 lines or 200 lines, it works!

## Getting Started

### Installation

```bash
npm install
```

### Run the App

```bash
npm start
```

Opens [http://localhost:3000](http://localhost:3000) in your browser.

### Customize the Template

Edit [src/pdfTemplate.js](src/pdfTemplate.js) to change:
- Layout and styling
- Add new fields
- Modify colors, fonts, and spacing
- Add tables, images, or lists
- Change page size or margins

## Available Scripts

### `npm start`

Runs the app in development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

The page will reload when you make changes.\
You may also see any lint errors in the console.

### `npm test`

Launches the test runner in the interactive watch mode.\
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

### `npm run eject`

**Note: this is a one-way operation. Once you `eject`, you can't go back!**

If you aren't satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you're on your own.

You don't have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn't feel obligated to use this feature. However we understand that this tool wouldn't be useful if you couldn't customize it when you are ready for it.

## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).

### Code Splitting

This section has moved here: [https://facebook.github.io/create-react-app/docs/code-splitting](https://facebook.github.io/create-react-app/docs/code-splitting)

### Analyzing the Bundle Size

This section has moved here: [https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size](https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size)

### Making a Progressive Web App

This section has moved here: [https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app](https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app)

### Advanced Configuration

This section has moved here: [https://facebook.github.io/create-react-app/docs/advanced-configuration](https://facebook.github.io/create-react-app/docs/advanced-configuration)

### Deployment

This section has moved here: [https://facebook.github.io/create-react-app/docs/deployment](https://facebook.github.io/create-react-app/docs/deployment)

### `npm run build` fails to minify

This section has moved here: [https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify](https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify)
