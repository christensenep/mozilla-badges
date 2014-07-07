(function () {

  var SVG_NS = "http://www.w3.org/2000/svg";

  var svgCache = {};
  var options = {};

  var $badge;
  var $badgeRaster;
  var $studio = document.getElementById('studio');

  var $template = document.getElementById('studio-template');
  var $palette = document.getElementById('studio-palette');
  var $mask = document.getElementById('studio-mask');
  var $glyph = document.getElementById('studio-glyph');

  var $glyphSelector;
  var $glyphSelectorButton;

  var $settings;
  var $settingsButton;

  var $help;

  $badgeRaster = new Image();
  $badgeRaster.id = 'raster';

  initSettings();
  initHelp();
  initGlyphSelector();

  window.addEventListener('load', function init () {
    document.getElementById('studio-output').appendChild($badgeRaster);

    $template.addEventListener('change', updateTemplate);
    $palette.addEventListener('change', updatePalette);
    $mask.addEventListener('change', updateMask);
    $glyph.addEventListener('change', updateGlyph);

    initStudio();

    initTemplates();
    initPalettes();
    initMasks();
    initOptions();
    initGlyphs();

    updateTemplate();
  });

  // ==[ General Methods ]======================================================

  /**
   *
   */
  function showError (err) {
    // TO DO - show errors :)
    console.err(err);
  }

  // ==[ Studio ]===============================================================

  /**
   *
   */
  function initStudio () {
    document.addEventListener('keydown', function(event) {
      if (event.keyCode === 27) { // Escape
        if ($settings && $settings.offsetWidth)
          closeSettings();
        else if ($help && $help.offsetWidth)
          closeHelp();
        else if ($glyphSelector && $glyphSelector.offsetWidth)
          closeGlyphSelector();
      }
    }, true);

    document.addEventListener('focus', function(event) {
      [$settings, $help, $glyphSelector].forEach(function ($overlay) {
        if ($overlay && $overlay.offsetWidth && !$overlay.contains(event.target)) {
          event.stopPropagation();
          $overlay.focus();
        }
      });
    }, true);
  }

  // ==[ Settings ]=============================================================

  /**
   *
   */
  function initSettings () {
    if ($settings)
      return false;

    $settingsButton = document.createElement('button');
    $settingsButton.className = 'settings fa fa-cog';
    $settingsButton.title = 'Settings';
    $settingsButton.addEventListener('click', openSettings);
    $studio.appendChild($settingsButton);

    $settings = importTemplate('settings').querySelector('#settings');
    $settings.querySelector('.header').appendChild(makeCloseButton(closeSettings));
    $studio.appendChild($settings);

    $settings.addEventListener('change', function (event) {
      var $target = event.target;
      handleUpdate($target.name, $target.value);
    });

    if (!window.localStorage)
      return;

    var $$options = $settings.querySelectorAll('select');
    for (var i = 0, l = $$options.length; i < l; i++) {
      var $option = $$options[i];
      var name = $option.name;
      var value = localStorage.getItem($option.name);
      for (var j = 0; j < $option.length; j++) {
        if ($option[j].value === value) {
          $option.selectedIndex = j;
          handleUpdate(name, value);
          break;
        }
      }
    }

    function handleUpdate (name, value) {
      switch (name) {
        case 'display':
          $studio.className = value;
          break;
        case 'badge-size':
          var scale = parseFloat(value);
          ['WebkitTransform', 'MozTransform', 'transform'].forEach(function(transform) {
            $badgeRaster && ($badgeRaster.style[transform] = 'scale(' + scale + ')');
          });
          break;
        default:
          name = null;
      }

      if (name && window.localStorage)
        localStorage.setItem(name, value);
    }
  }

  /**
   *
   */
  function openSettings () {
    if (!$settings)
      initSettings();

    $settings.classList.remove('hidden');
    $settings.focus();
  }

  /**
   *
   */
  function closeSettings () {
    if (!$settings)
      return;

    $settings.classList.add('hidden');
    $settingsButton.focus();
  }

  // ==[ Help ]=================================================================

  /**
   *
   */
  function initHelp () {
    if ($help)
      return false

    $help = importTemplate('help').querySelector('#help');
    $help.querySelector('.header').appendChild(makeCloseButton(closeHelp));
    $studio.appendChild($help);

    $studio.addEventListener('click', function (event) {
      var $target = (event.target || {});

      if ($target.nodeName !== 'A')
        $target = $target.parentNode;

      if (!$target || ($target.nodeName !== 'A') || !$target.classList.contains('help'))
        return;

      event.preventDefault();
      openHelp($target.getAttribute('href').substr(1))
    });

    $help.addEventListener('focus', function(event) {
      var $target = event.target;
      if ($target.nodeName !== 'DD')
        return;
      $help.setAttribute('return', '#'+$target.id);
    }, true);
  }

  /**
   *
   */
  function openHelp (section) {
    if (!$help)
      initHelp();

    $help.classList.remove('hidden');
    $help.focus();
    if (section) {
      var $section = document.getElementById(section);
      if ($section)
        $section.focus();
    }
  }

  /**
   *
   */
  function closeHelp () {
    if (!$settings)
      return;

    $help.classList.add('hidden');

    var returnTo = $help.getAttribute('return');
    $help.removeAttribute('return');

    if (returnTo) {
      var $returnTo = $studio.querySelector('[href$="'+returnTo+'"]');
      if ($returnTo)
        $returnTo.focus();
    }
  }

  // ==[ Glyph Selector ]=======================================================

  /**
   *
   */
  function initGlyphSelector () {
    if ($glyphSelector)
      return false;

    var glyphLog = [];

    $glyphSelectorButton = document.createElement('button');
    $glyphSelectorButton.id = 'search-glyphs';
    $glyphSelectorButton.type = 'button';
    $glyphSelectorButton.innerHTML = '<i class="fa fa-search"></i> Search';
    $glyphSelectorButton.addEventListener('click', openGlyphSelector);

    $glyph.parentNode.insertBefore($glyphSelectorButton, $glyph.nextSibling);

    var $$options = $glyph.querySelectorAll('option');

    $glyphSelector = importTemplate('glyph-selector', function ($template) {

      var $list = $template.querySelector('ul');

      for (var i = 0, l = $$options.length; i < l; i++) {
        (function ($option, index) {
          var value = $option.getAttribute('data-glyph') || '';
          var id = 'glyph-selector-item-' + value;
          var tags = $option.getAttribute('data-tags') || '';

          var $node = importTemplate('glyph-selector-item', function ($template) {
            var $input = $template.querySelector('input');
            $input.id = id;
            $input.value = index;

            var checked = $glyph.selectedIndex === index;
            $input[checked ? 'setAttribute' : 'removeAttribute']('checked', 'checked');

            var $label = $template.querySelector('label');
            $label.id = id + '-label';
            $label.className = 'fa fa-' + value;
            $label.setAttribute('for', id);
            $label.setAttribute('title', $option.text);
          }).querySelector('li');

          $list.appendChild($node);

          glyphLog.push({
            id: id,
            value: value,
            tags: tags
          });
        })($$options[i], i);
      }

    }).querySelector('#glyph-selector');

    var $filter = $glyphSelector.querySelector('input');
    var filterTimer;

    function filterGlyphs () {
      clearTimeout(filterTimer);

      filterTimer = setTimeout(function () {
        var query = ($filter.value || '').toLowerCase().replace(/\s*,\s*/, ',').split(',');
        var queryRE = new RegExp('(^|,)[^,]*' + query.join('[^,]*|[^,]*') + '[^,]*(,|$)', 'i');

        for (var i = 0, l = glyphLog.length; i < l; i++) {
          var entry = glyphLog[i];

          if (!entry.el)
            entry.el = document.getElementById(entry.id).parentNode;

          var matched = queryRE.test(entry.value + ', ' + entry.tags);
          entry.el.style.display = (matched ? '' : 'none');
        }
      }, 250);
    }

    $glyphSelector.querySelector('.header').appendChild(makeCloseButton(closeGlyphSelector));
    $studio.appendChild($glyphSelector);

    $glyphSelector.addEventListener('change', function (event) {
      if (event.target === $filter)
        return filterGlyphs();

      event.stopPropagation();
      var index = event.target.value;
      $glyph.selectedIndex = index;

      updateGlyph();
    });

    $glyphSelector.addEventListener('click', function (event) {
      if (event.target.nodeName.toLowerCase() !== 'label')
        return;

      event.stopPropagation();
      closeGlyphSelector();
    });

    $glyphSelector.addEventListener('keydown', function (event) {
      if (event.target === $filter)
        return filterGlyphs();

      if (event.keyCode === 13) { // Enter
        if (event.target.name)
          $glyph.selectedIndex = event.target.value;
        return updateGlyph(closeGlyphSelector);
      }

      if (event.keyCode === 38 || event.keyCode === 40) { // Up / Down
        event.preventDefault();

        var $container = event.target.parentNode.parentNode;
        var itemSize = event.target.parentNode.offsetWidth;
        var containerSize = $container.offsetWidth;
        var rowCount = Math.floor(containerSize / itemSize);
        var currentIndex = parseInt(event.target.value);
        var newIndex = currentIndex;
        var altFinder;

        if (event.keyCode === 38) {
          // Move up a row
          newIndex = currentIndex - rowCount;
          altFinder = 'firstElementChild';
        } else {
          // Move down a row
          newIndex = currentIndex + rowCount;
          altFinder = 'lastElementChild';
        }

        var newItem = $container.querySelector('input[value="'+newIndex+'"]') ||
                      $container[altFinder].querySelector('input');

        $glyph.selectedIndex = newItem.value;
        newItem.checked = true;
        newItem.focus();
        rasterize();
      }
    });

    $glyphSelector.addEventListener('search', function (event) {
      if (event.target === $filter)
        return filterGlyphs();
    })

    $glyphSelector.addEventListener('focus', function (event) {
      if (event.target !== $glyphSelector)
        return;

      event.stopPropagation();
      $filter.focus();
    }, true);

    $glyph.addEventListener('change', function (event) {
      var $selectorItem = document.getElementById('glyph-selector-item-' + this.value);
      if ($selectorItem) {
        $selectorItem.click();
      }
    });
  }

  /**
   *
   */
  function openGlyphSelector () {
    if (!$glyphSelector)
      initGlyphSelector();

    $glyphSelector.classList.remove('hidden');

    var glyph = getCurrentGlyphValue()
    if (glyph)
      document.getElementById('glyph-selector-item-' + glyph + '-label').focus();

    $glyphSelector.focus();
  }

  /**
   *
   */
  function closeGlyphSelector () {
    if (!$glyphSelector)
      return;

    $glyphSelector.classList.add('hidden');
    $glyphSelectorButton.focus();
  }

  // ==[ Templates ]============================================================

  /**
   *
   */
  function initTemplates () {

  }

  /**
   *
   */
  function getCurrentTemplate () {
    return $template.value;
  }

  /**
   *
   */
  function getCurrentTemplatePath () {
    return $template[$template.selectedIndex].getAttribute('data-path');
  }

  /**
   *
   */
  function updateTemplate (callback) {
    callback = cb(callback);

    loadSVG(getCurrentTemplatePath(), function (err, $svg) {
      if (err)
        return showError(err);

      $badge = $svg;

      extractOptions();
      setCustomPalette($svg);
      $badgeRaster.style.visibility = 'hidden';
      rasterize(function () {
        updatePalette(function() {
          updateMask(function () {
            $badgeRaster.style.visibility = '';
            callback()
          });
        });
      });
    });
  }

  // ==[ Palettes ]=============================================================

  function Palette (colors) {
    this._colors = {};
    if (colors) {
      for (var color in colors) {
        if (colors.hasOwnProperty(color)) {
          this._colors[color] = Palette.parseColor(colors[color]);
        }
      }
    }
    if (!this._colors.hasOwnProperty('glyph'))
      this._colors['glyph'] = '#000000';
  }

  Palette.prototype.toNode = function (id) {
    var content = [];
    for (var color in this._colors) {
      if (this._colors.hasOwnProperty(color)) {
        content.push('.color-' + color + ' { fill: ' + this._colors[color] + '; }');
      }
    }

    var $node = document.createElement('style');
    $node.type = 'text/css';
    $node.id = id || 'palette';
    $node.textContent = content.join('\n');
    return $node;
  }

  Palette.prototype.colors = function () {
    return Object.keys(this._colors);
  }

  Palette.prototype.color = function (name) {
    return this._colors[name] || '#000';
  }

  Palette.parseColor = function (str) {
    // Should probably be a bit more robust about this!
    if (!/^#[a-f0-9]{3}$/i.test(str))
      return str.toLowerCase();
    return '#' + str.charAt(1) + str.charAt(1)
               + str.charAt(2) + str.charAt(2)
               + str.charAt(3) + str.charAt(3);
  }

  Palette.fromDataset = function (dataset) {
    var colors = {};
    for (var item in dataset) {
      if (/^color\w+/i.test(item)) {
        var color = item
                      .replace(/^color(\w)/i, function (m, c) { return c.toLowerCase(); })
                      .replace(/[A-Z]/, function (m) { return '-' + m.toLowerCase(); });
        colors[color] = dataset[item];
      }
    }
    return new Palette(colors);
  }

  Palette.fromSVG = function ($svg) {
    var colors = {};
    var $node = $svg.getElementById('palette');
    if (!$node || $node.nodeName !== 'style')
      return new Palette();

    var $stylesheet = document.createElement('style');
    $stylesheet.setAttribute('media', 'print');
    $stylesheet.appendChild(document.createTextNode($node.textContent));
    document.head.appendChild($stylesheet);
    var sheet = $stylesheet.sheet;
    document.head.removeChild($stylesheet);

    var rules = sheet.rules || sheet.cssRules;
    for (var i = 0, l = rules.length; i < l; i++) {
      var rule = rules[i];
      var selector = rule.selectorText;
      if (/^\.color-/.test(selector)) {
        var key = selector.replace(/^\.color-/, '');
        var value = rule.style.fill || '#000';
        colors[key] = value;
      }
    }

    return new Palette(colors);
  }

  /**
   *
   */
  function initPalettes () {
    var $custom = document.createElement('option');
    $custom.disabled = true;
    $custom.value = '';
    $custom.text = 'Custom';
    $custom.id = 'custom-color-option';
    $palette.options.add($custom);

    var $container = document.getElementById('custom-palette');

    $palette.addEventListener('change', function () {
      // var isCustom = (this.options[this.selectedIndex] === $custom);
      // $custom.disabled = !isCustom;

      setCustomColors();
      updatePalette();
    });

    var changeTimer;

    $container.addEventListener('change', function (event) {
      var $$inputs = $container.querySelectorAll('input');

      for (var i = 0, l = $$inputs.length; i < l; i++) {
        var $input = $$inputs[i];
        var color = $input.getAttribute('data-color');
        $custom.setAttribute('data-color-'+color, $input.value);
      }

      $custom.disabled = false;
      $palette.selectedIndex = $palette.options.length - 1;

      updatePalette();
    });

    setCustomColors();

    if (Object.keys($container.dataset).length) {
      palette = Palette.fromDataset($container.dataset)
      $custom.disabled = false;
      $palette.selectedIndex = $palette.options.length - 1;
      setCustomColors(palette);
    }
  }

  /**
   *
   */
  function getCurrentPalette () {
    var $option = $palette.options[$palette.selectedIndex];
    return Palette.fromDataset($option.dataset);
  }

  /**
   *
   */
  function updatePalette (callback) {
    callback = cb(callback);

    var $oldPalette = $badge.getElementById('palette');
    var $newPalette = getCurrentPalette().toNode();

    if ($oldPalette) {
      $oldPalette.parentNode.insertBefore($newPalette, $oldPalette);
      $oldPalette.parentNode.removeChild($oldPalette);
    } else {
      var $defs = $badge.querySelector('defs') || document.createElement('defs');

      if (!$defs.parentNode)
        $badge.insertBefore($defs, $badge.childNodes[0]);

      $defs.appendChild($newPalette)
    }

    updateGlyph(callback);
  }

  /**
   *
   */
  function setCustomPalette ($svg, callback) {
    callback = cb(callback);

    var colors = Palette.fromSVG($svg).colors();

    var $container = document.getElementById('custom-palette');
    var display = $container.style.display;
    $container.innerHTML = '';
    $container.style.display = 'none';
    $container.className = 'item';

    for (var i = 0, l = colors.length; i < l; i++) {
      var name = colors[i];
      var label = name.replace(/(^|-)(\w)/g, function (m, x, c) {
        return (x ? ' ' : '') + c.toUpperCase();
      });

      $container.appendChild(importTemplate('custom-color', function ($template) {
        var $input = $template.querySelector('input');
        $input.name = 'colors[' + name + ']';
        $input.setAttribute('data-color', name);
        $input.id = 'custom-color-picker-' + name;
        var $label = $template.querySelector('span');
        $label.textContent = label;
      }));
    }

    if (colors.length)
      $container.style.display = display;

    setCustomColors();
  }

  /**
   *
   */
  function setCustomColors (palette) {
    var $custom = document.getElementById('custom-color-option');
    var $option = $palette.options[$palette.selectedIndex];

    if (!palette)
      palette = Palette.fromDataset($option.dataset);

    var colors = palette.colors();

    for (var i = 0, l = colors.length; i < l; i++) {
      var colorName = colors[i];
      var colorValue = palette.color(colorName);

      if ($custom.disabled || $option === $custom)
        $custom.setAttribute('data-color-' + colorName, colorValue);

      var $input = document.getElementById('custom-color-picker-' + colorName);
      if ($input)
        $input.value = colorValue;
    }
  }

  // ==[ Masks ]================================================================

  /**
   *
   */
  function initMasks () {
    return;

    var $button = document.createElement('button');
    $button.type = 'button';
    $button.innerHTML = '<i class="fa fa-image"></i> Custom';
    $button.addEventListener('click', function () {
      var $input = document.createElement('input');
      $input.type = 'file';
      $input.accept = 'image/*';
      $input.addEventListener('change', function () {
        var file = this.files[0];
        if (!file.type.match('image.*'))
          return false;

        var reader = new FileReader();
        reader.onload = function (evt) {
          if (evt.type !== 'load')
            return;

          var data = reader.result;
          var name = file.name;
          var id = 'custom-' + Date.now();
          var path = $mask.dataset.path + '/' + id + '.svg';

          var $img = new Image();
          $img.onload = function () {
            var $svg = document.createElementNS(SVG_NS, 'svg');

            var $g = document.createElementNS(SVG_NS, 'g');
            $g.id = 'mask';
            $svg.appendChild($g);

            var $image = convertImgToSvg($img, 'cover');
            $g.appendChild($image);

            svgCache[path] = $svg;

            var $group = $mask.getElementsByTagName('optgroup')[0];
            if (!$group) {
              $group = document.createElement('optgroup');
              $group.label = 'Custom';
              $mask.appendChild($group);
            }

            var $option = document.createElement('option');
            $option.value = id;
            $option.text = name;
            $group.appendChild($option);
            $mask.selectedIndex = $mask.options.length - 1;
            updateMask();
          }
          $img.src = data;
        }
        reader.onerror = function () {
          alert('Failed to load file ' + file.name);
        }
        reader.readAsDataURL(this.files[0]);
      });
      $input.click();
      // alert('Custom!');
    });

    $mask.parentNode.insertBefore($button, $mask.nextSibling);

  }

  /**
   *
   */
  function getCurrentMask () {
    return $mask.value;
  }

  /**
   *
   */
  function getCurrentMaskPath () {
    return $mask[$mask.selectedIndex].getAttribute('data-path');
  }

  /**
   *
   */
  function updateMask (callback) {
    callback = cb(callback);

    var mask = getCurrentMask();

    if (!mask) {
        var $svg = document.createElementNS(SVG_NS, 'svg');
        var $g = document.createElementNS(SVG_NS, 'g');
        $g.id = 'mask';
        $svg.appendChild($g);
        return done(null, $svg);
    }

    loadSVG(getCurrentMaskPath(), done);

    function done (err, $svg) {
      if (err)
        return showError(err);

      var $oldMask = $badge.querySelector('#mask');
      var $newMask = $svg.querySelector('#mask');

      $oldMask.parentNode.insertBefore($newMask, $oldMask);
      $oldMask.parentNode.removeChild($oldMask);

      rasterize(callback);
    }
  }

  // ==[ Options ]==============================================================

  /**
   *
   */
  function initOptions () {
    var $options = document.getElementById('options');
    for (var key in $options.dataset) {
      options[key] = ($options.dataset[key] === 'on');
    }

    if ($badge)
      extractOptions();

    $options.addEventListener('change', function (event) {
      event.stopPropagation();
      var option = event.target.getAttribute('data-property');
      if (!options.hasOwnProperty(option))
        return;

      options[option] = !!event.target.checked;
      setOptions();
    });
  }

  /**
   *
   */
  function extractOptions () {
    var $options = document.getElementById('options');
    $options.innerHTML = '';

    var $optional = $badge.querySelectorAll('.optional');

    if (!$optional.length) {
      $options.innerHTML = '<i>None</l>';
      return;
    }

    for (var i = 0, l = $optional.length; i < l; i++) {
      var $option = $optional[i];
      var label = $option.getAttribute('title');
      var name = $option.id;
      var enabled = ($option.getAttribute('display') !== 'none');
      if (!options.hasOwnProperty(name))
        options[name] = enabled;

      $option[!!options[name] ? 'removeAttribute' : 'setAttribute']('display', 'none');

      $options.appendChild(importTemplate('option', function ($template) {
        var $$inputs = $template.querySelectorAll('input');
        var $hidden = $$inputs[0];
        var $checkbox = $$inputs[1];

        // Double input hack:
        // If the checkbox is unchecked it's state won't be sent to the server,
        // so the next time we come to edit the design the default state will be
        // used instead of however the user left it. By including the hidden
        // input first, an 'off' value will be sent, and overridden by an 'on'
        // value should the checkbox be checked.

        $hidden.name = 'options[' + name + ']';
        $hidden.value = 'off';

        $checkbox.name = 'options[' + name + ']';
        $checkbox.value = 'on';
        $checkbox.setAttribute('data-property', name);
        $checkbox.checked = !!options[name];

        var $label = $template.querySelector('span');
        $label.textContent = label;
      }));
    }
  }

  /**
   *
   */
  function setOptions (callback) {
    callback = cb(callback);

    if (!$badge)
      return callback();

    for (var option in options) {
      if (options.hasOwnProperty(option)) {
        var $node = $badge.getElementById(option);
        var visible = !!options[option];
        $node && ($node[visible ? 'removeAttribute' : 'setAttribute']('display', 'none'));
      }
    }

    rasterize(callback)
  }

  // ==[ Glyphs ]===============================================================

  /**
   *
   */
  function initGlyphs () {

  }

  /**
   *
   */
  function getCurrentGlyph () {
    return $glyph[$glyph.selectedIndex].getAttribute('data-glyph');
  }

  /**
   *
   */
  function getCurrentGlyphValue () {
    if (!$glyph.value)
      return '';

    var $i = document.createElement('i');
    $i.className = 'fa fa-' + getCurrentGlyph();
    document.body.appendChild($i);
    var chr = window.getComputedStyle($i, ':before').content;
    document.body.removeChild($i);

    chr = chr.replace(/"/g, '');
    return chr;
  }

  /**
   *
   */
  function updateGlyph (callback) {
    var glyph = getCurrentGlyphValue();

    if (!glyph)
      return setGlyphImage(null, callback);

    var $canvas = document.createElement('canvas');
    $canvas.width = parseInt($badgeRaster.offsetWidth);
    $canvas.height = parseInt($badgeRaster.offsetHeight);

    var ctx = $canvas.getContext('2d');
    ctx.font = parseInt($canvas.width / 3) + "px FontAwesome";
    ctx.fillStyle = getCurrentPalette().color('glyph');
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.shadowColor = "rgba(0,0,0,0.5)";
    ctx.shadowOffsetX = 0;
    ctx.shadowOffsetY = 0;
    ctx.shadowBlur = 5;

    ctx.fillText(glyph, $canvas.width / 2, $canvas.height / 2);

    var $image = new Image();
    $image.onload = function () {
      setGlyphImage($image, callback);
    }
    $image.src = $canvas.toDataURL("image/png");
    // $image.src = "./media/images/cheese.jpg";
  }

  /**
   *
   */
  function setGlyphImage ($img, callback) {
    callback = cb(callback);

    var $newGlyph = document.createElementNS(SVG_NS, 'g');
    $newGlyph.id = 'glyph';

    if (!$img)
      return done();

    var $glyph = convertImgToSvg($img);
    $newGlyph.appendChild($glyph);

    done();

    function done () {
      var $oldGlyph = $badge.getElementById('glyph');

      $oldGlyph.parentNode.insertBefore($newGlyph, $oldGlyph);
      $oldGlyph.parentNode.removeChild($oldGlyph);

      rasterize(callback);
    }
  }

  // ==[ Helpers ]==============================================================

  /**
   *
   */
  function rasterize (callback) {
    callback = cb(callback);

    var $svg = $badge.cloneNode(true);

    var $canvas = document.createElement('canvas');
    $canvas.width = parseInt($svg.getAttribute('width'));
    $canvas.height = parseInt($svg.getAttribute('height'));

    var ctx = $canvas.getContext('2d');
    var svg_xml = (new XMLSerializer()).serializeToString($svg);

    /*
    // This is the 'official' way of doing this. However, Firefox seems to have
    // an issue referencing relative fragment URIs created by `createObjectURL`.
    // So we're using a base64 encoding hack instead :( Worth noting that if
    // there are non-standard unicode characters in the XML, it'll die a death.

    var DOMURL = window.URL || window.webkitURL || window;
    var blob = new Blob([svg_xml], {type: 'image/svg+xml;charset=utf-8'});
    var url = DOMURL.createObjectURL(blob);
    */

    var url = 'data:image/svg+xml;base64,' + btoa(svg_xml);

    var $img = new Image();
    $img.onload = function() {
      ctx.drawImage($img, 0, 0);
      $badgeRaster.src = $canvas.toDataURL("image/png");
      document.getElementById('studio-image').value = $badgeRaster.src;
      callback();
    }
    $img.src = url;
  }

  /**
   *
   */
  function cb (fn) {
    if (typeof fn === 'function')
      return fn;
    return function () {};
  }

  /**
   *
   */
  function load (url, method, callback) {
    var request = new XMLHttpRequest();

    request.onload = function () {
      callback(null, request.responseXML || request.responseText, request);
    }

    request.onerror = function (err) {
      callback(err, null, request);
    }

    request.open(method, url, true);
    request.send();
  }

  /**
   *
   */
  function loadSVG (path, callback) {
    if (svgCache[path])
      return callback(null, svgCache[path].cloneNode(true));

    load(path, 'GET', function (err, $doc, request) {
      if (err)
        return callback(err);

      if (!$doc || typeof $doc === 'string')
        return callback(new Error('Not valid SVG'));

      svgCache[path] = $doc.getElementsByTagName('svg')[0];
      callback(null, svgCache[path].cloneNode(true));
    })
  }

  /**
   *
   */
  function importTemplate (name, builder) {
    var $template = document.getElementById(name + '-template');
    if (typeof builder === 'function')
      builder($template.content);
    return document.importNode($template.content, true);
  }

  /**
   *
   */
  function makeCloseButton (callback) {
    var $template = importTemplate('close-button');
    $template.querySelector('button').addEventListener('click', callback);
    return $template;
  }

  /**
   *
   */
  function convertImgToSvg ($img) {
    var iWidth = $img.width;
    var iHeight = $img.height;

    var rWidth = $badgeRaster.width;
    var rHeight = $badgeRaster.height;

    var box = $badge.getAttribute('viewBox').split(' ');

    var bWidth = parseInt(box[2]);
    var bHeight = parseInt(box[3]);

    var cx = bWidth / 2 + parseInt(box[0]);
    var cy = bHeight / 2 + parseInt(box[1]);

    var gWidth = iWidth / (rWidth / bWidth);
    var gHeight = iHeight / (rHeight / bHeight);

    var gx = cx - (gWidth / 2);
    var gy = cy - (gHeight / 2);

    var $image = document.createElementNS(SVG_NS, 'image');
    $image.setAttribute('xlink:href', $img.src);
    $image.setAttribute('x', gx);
    $image.setAttribute('y', gy);
    $image.setAttribute('width', gWidth);
    $image.setAttribute('height', gHeight);

    return $image;
  }

})();