const { JSDOM } = require('jsdom');
const path = require('path');

describe('navList', () => {
  test('produces links with depth classes based on nesting', () => {
    const dom = new JSDOM('<!doctype html><html><body></body></html>');
    const { window } = dom;
    const $ = require('jquery')(window);

    global.window = window;
    global.document = window.document;
    global.$ = $;
    global.jQuery = $;

    require(path.resolve(__dirname, '../assets/js/util.js'));

    const $nav = $(
      `<nav>
        <ul>
          <li><a href="#home">Home</a></li>
          <li>
            <a href="#about">About</a>
            <ul>
              <li><a href="#team">Team</a></li>
            </ul>
          </li>
        </ul>
      </nav>`
    );

    const result = $nav.navList();
    const frag = JSDOM.fragment(result);
    const links = frag.querySelectorAll('a');

    expect(links.length).toBe(3);
    expect(links[0].classList.contains('depth-0')).toBe(true);
    expect(links[1].classList.contains('depth-0')).toBe(true);
    expect(links[2].classList.contains('depth-1')).toBe(true);
  });
});
