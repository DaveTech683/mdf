(function() {
  "use strict";

  /**
   * Apply .scrolled class to the body as the page is scrolled down
   */
  function toggleScrolled() {
    const selectBody = document.querySelector('body');
    const selectHeader = document.querySelector('#header');

    if (!selectBody || !selectHeader) return;

    if (
      !selectHeader.classList.contains('scroll-up-sticky') &&
      !selectHeader.classList.contains('sticky-top') &&
      !selectHeader.classList.contains('fixed-top')
    ) return;

    window.scrollY > 100
      ? selectBody.classList.add('scrolled')
      : selectBody.classList.remove('scrolled');
  }

  // document.addEventListener('scroll', toggleScrolled);
  // window.addEventListener('load', toggleScrolled);


  /**
   * Mobile nav toggle
   * Safe version: only runs if the old .mobile-nav-toggle exists.
   * Your current layout uses .mdf-hamburger, which is handled in your template.
   */
  const mobileNavToggleBtn = document.querySelector('.mobile-nav-toggle');
  const ul = document.getElementById('viewing');

  function mobileNavToogle() {
    document.body.classList.toggle('mobile-nav-active');

    if (mobileNavToggleBtn) {
      mobileNavToggleBtn.classList.toggle('bi-list');
      mobileNavToggleBtn.classList.toggle('bi-x');
    }

    if (ul) {
      ul.style.display = ul.style.display === 'none' ? 'block' : 'none';
    }
  }

  if (mobileNavToggleBtn) {
    mobileNavToggleBtn.addEventListener('click', mobileNavToogle);
  }


  /**
   * Preloader
   */
  const preloader = document.querySelector('#preloader');

  if (preloader) {
    window.addEventListener('load', () => {
      preloader.remove();
    });
  }


  /**
   * Scroll top button
   */
  let scrollTop = document.querySelector('.scroll-top');

  function toggleScrollTop() {
    if (scrollTop) {
      window.scrollY > 100
        ? scrollTop.classList.add('active')
        : scrollTop.classList.remove('active');
    }
  }

  if (scrollTop) {
    scrollTop.addEventListener('click', (e) => {
      e.preventDefault();

      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    });

    window.addEventListener('load', toggleScrollTop);
    document.addEventListener('scroll', toggleScrollTop);
  }


  /**
   * Animation on scroll function and init
   */
  function aosInit() {
    if (typeof AOS !== 'undefined') {
      AOS.init({
        duration: 600,
        easing: 'ease-in-out',
        once: true,
        mirror: false
      });
    }
  }

  window.addEventListener('load', aosInit);


  /**
   * Initiate glightbox
   */
  if (typeof GLightbox !== 'undefined') {
    GLightbox({
      selector: '.glightbox'
    });
  }


  /**
   * Init swiper sliders
   */
  function initSwiper() {
    if (typeof Swiper === 'undefined') return;

    document.querySelectorAll('.swiper').forEach(function(swiper) {
      const configElement = swiper.querySelector('.swiper-config');

      if (!configElement) return;

      try {
        let config = JSON.parse(configElement.innerHTML.trim());
        new Swiper(swiper, config);
      } catch (error) {
        console.warn('Swiper config error:', error);
      }
    });
  }

  window.addEventListener('load', initSwiper);


  /**
   * Frequently Asked Questions Toggle
   */
  document.querySelectorAll('.faq-item h3, .faq-item .faq-toggle').forEach((faqItem) => {
    faqItem.addEventListener('click', () => {
      if (faqItem.parentNode) {
        faqItem.parentNode.classList.toggle('faq-active');
      }
    });
  });


  /**
   * Animate the skills items on reveal
   */
  let skillsAnimation = document.querySelectorAll('.skills-animation');

  if (typeof Waypoint !== 'undefined') {
    skillsAnimation.forEach((item) => {
      new Waypoint({
        element: item,
        offset: '80%',
        handler: function(direction) {
          let progress = item.querySelectorAll('.progress .progress-bar');

          progress.forEach(el => {
            el.style.width = el.getAttribute('aria-valuenow') + '%';
          });
        }
      });
    });
  }


  /**
   * Init isotope layout and filters
   */
  if (typeof imagesLoaded !== 'undefined' && typeof Isotope !== 'undefined') {
    document.querySelectorAll('.isotope-layout').forEach(function(isotopeItem) {
      let layout = isotopeItem.getAttribute('data-layout') ?? 'masonry';
      let filter = isotopeItem.getAttribute('data-default-filter') ?? '*';
      let sort = isotopeItem.getAttribute('data-sort') ?? 'original-order';
      let container = isotopeItem.querySelector('.isotope-container');

      if (!container) return;

      let initIsotope;

      imagesLoaded(container, function() {
        initIsotope = new Isotope(container, {
          itemSelector: '.isotope-item',
          layoutMode: layout,
          filter: filter,
          sortBy: sort
        });
      });

      isotopeItem.querySelectorAll('.isotope-filters li').forEach(function(filters) {
        filters.addEventListener('click', function() {
          const activeFilter = isotopeItem.querySelector('.isotope-filters .filter-active');

          if (activeFilter) {
            activeFilter.classList.remove('filter-active');
          }

          this.classList.add('filter-active');

          if (initIsotope) {
            initIsotope.arrange({
              filter: this.getAttribute('data-filter')
            });
          }

          if (typeof aosInit === 'function') {
            aosInit();
          }
        }, false);
      });
    });
  }


  /**
   * Correct scrolling position upon page load for URLs containing hash links.
   */
  window.addEventListener('load', function(e) {
    if (window.location.hash) {
      const section = document.querySelector(window.location.hash);

      if (section) {
        setTimeout(() => {
          let scrollMarginTop = getComputedStyle(section).scrollMarginTop;

          window.scrollTo({
            top: section.offsetTop - parseInt(scrollMarginTop),
            behavior: 'smooth'
          });
        }, 100);
      }
    }
  });


  /**
   * Navmenu Scrollspy
   */
  let navmenulinks = document.querySelectorAll('.navmenu a');

  function navmenuScrollspy() {
    navmenulinks.forEach(navmenulink => {
      if (!navmenulink.hash) return;

      let section = document.querySelector(navmenulink.hash);

      if (!section) return;

      let position = window.scrollY + 200;

      if (
        position >= section.offsetTop &&
        position <= section.offsetTop + section.offsetHeight
      ) {
        document.querySelectorAll('.navmenu a.active').forEach(link => {
          link.classList.remove('active');
        });

        navmenulink.classList.add('active');
      } else {
        navmenulink.classList.remove('active');
      }
    });
  }

  window.addEventListener('load', navmenuScrollspy);
  document.addEventListener('scroll', navmenuScrollspy);


  /**
   * Product image switcher
   */
  const shoeslide = [
    'assets/img/Mask Group 9.png',
    'assets/img/hero-img-2.jpg',
    'assets/img/Mask Group 9.png',
    'assets/img/hero-img-2.jpg',
    'assets/img/Mask Group 9.png',
    'assets/img/hero-img-2.jpg',
    'assets/img/Mask Group 9.png',
    'assets/img/hero-img-2.jpg',
    'assets/img/Mask Group 9.png',
    'assets/img/hero-img-2.jpg',
    'assets/img/Mask Group 9.png',
    'assets/img/hero-img-2.jpg'
  ];

  const accessoryslide = [
    'assets/img/Mask Group 12.png',
    'assets/img/Mask Group 12.png',
    'assets/img/Mask Group 12.png',
    'assets/img/Mask Group 12.png',
    'assets/img/Mask Group 12.png',
    'assets/img/Mask Group 12.png',
    'assets/img/Mask Group 12.png',
    'assets/img/hero-img-2.jpg',
    'assets/img/Mask Group 12.png',
    'assets/img/hero-img-2.jpg',
    'assets/img/Mask Group 12.png',
    'assets/img/hero-img-2.jpg'
  ];

  const bouquetslide = [
    'assets/img/Mask Group 9.png',
    'assets/img/hero-img-3.jpg',
    'assets/img/Mask Group 9.png',
    'assets/img/hero-img-3.jpg',
    'assets/img/Mask Group 9.png',
    'assets/img/hero-img-3.jpg',
    'assets/img/Mask Group 9.png',
    'assets/img/hero-img-3.jpg',
    'assets/img/Mask Group 9.png',
    'assets/img/hero-img-3.jpg',
    'assets/img/Mask Group 9.png',
    'assets/img/hero-img-3.jpg'
  ];

  const purseslide = [
    'assets/img/Mask Group 11.png',
    'assets/img/hero-img-2.jpg',
    'assets/img/Mask Group 11.png',
    'assets/img/hero-img-2.jpg',
    'assets/img/Mask Group 11.png',
    'assets/img/hero-img-2.jpg',
    'assets/img/Mask Group 11.png',
    'assets/img/hero-img-2.jpg',
    'assets/img/Mask Group 11.png',
    'assets/img/hero-img-2.jpg',
    'assets/img/Mask Group 11.png',
    'assets/img/hero-img-2.jpg'
  ];

  const image1 = document.getElementById("pid1");
  const image2 = document.getElementById("pid2");
  const image3 = document.getElementById("pid3");
  const image4 = document.getElementById("pid4");
  const image5 = document.getElementById("pid5");
  const image6 = document.getElementById("pid6");
  const image7 = document.getElementById("pid7");
  const image8 = document.getElementById("pid8");
  const image9 = document.getElementById("pid9");
  const image10 = document.getElementById("pid10");
  const image11 = document.getElementById("pid11");
  const image12 = document.getElementById("pid12");

  const productImages = [
    image1,
    image2,
    image3,
    image4,
    image5,
    image6,
    image7,
    image8,
    image9,
    image10,
    image11,
    image12
  ];

  function updateProductImages(slideArray) {
    productImages.forEach((image, index) => {
      if (image && slideArray[index]) {
        image.src = slideArray[index];
      }
    });
  }

  function shoes() {
    updateProductImages(shoeslide);
  }

  function accessories() {
    updateProductImages(accessoryslide);
  }

  function bouquets() {
    updateProductImages(bouquetslide);
  }

  function purse() {
    updateProductImages(purseslide);
  }

  window.shoes = shoes;
  window.accessories = accessories;
  window.bouquets = bouquets;
  window.purse = purse;


  /**
   * Cart image click effect
   */
  const pics = document.getElementById("cart-img");

  function navclick() {
    if (!pics) return;

    pics.style.height = '4.3vh';
    pics.style.transition = '1s';
  }

  window.navclick = navclick;

})();