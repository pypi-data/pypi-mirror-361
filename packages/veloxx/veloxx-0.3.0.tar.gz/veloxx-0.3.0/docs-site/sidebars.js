/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */

// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  // By default, Docusaurus generates a sidebar from the docs folder structure
  tutorialSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Getting Started',
      items: [
        'getting-started/installation',
        'getting-started/quick-start',
      ],
    },
    {
      type: 'category',
      label: 'API Reference',
      items: [
        'api/rust',
        'api/python',
        'api/javascript',
      ],
    },
    {
      type: 'category',
      label: 'Examples & Guides',
      items: [
        {
          type: 'link',
          label: 'Data Processing Examples',
          href: 'https://github.com/Conqxeror/veloxx/tree/main/examples',
        },
        {
          type: 'link',
          label: 'Advanced Tutorials',
          href: 'https://github.com/Conqxeror/veloxx/tree/main/docs',
        },
      ],
    },
    {
      type: 'category',
      label: 'Performance',
      items: [
        'performance/benchmarks',
      ],
    },
  ],
};

module.exports = sidebars;