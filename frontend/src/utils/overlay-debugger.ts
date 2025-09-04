/**
 * Utility functions to debug and fix overlay-related UI responsiveness issues
 */

export interface OverlayInfo {
  element: HTMLElement;
  selector: string;
  zIndex: string;
  opacity: string;
  display: string;
  pointerEvents: string;
  position: string;
}

/**
 * Get all potentially problematic overlays in the document
 */
export function getProblematicOverlays(): OverlayInfo[] {
  const selectors = [
    '[data-scope="drawer"][data-part="backdrop"]',
    '.chakra-modal__overlay',
    '[data-portal]',
    '.chakra-drawer__overlay',
    '.chakra-modal__backdrop',
  ];

  const overlays: OverlayInfo[] = [];

  selectors.forEach(selector => {
    const elements = document.querySelectorAll(selector);
    elements.forEach(element => {
      const el = element as HTMLElement;
      const computedStyle = window.getComputedStyle(el);
      
      overlays.push({
        element: el,
        selector,
        zIndex: computedStyle.zIndex,
        opacity: computedStyle.opacity,
        display: computedStyle.display,
        pointerEvents: computedStyle.pointerEvents,
        position: computedStyle.position,
      });
    });
  });

  return overlays;
}

/**
 * Check if there are any overlays that might be blocking interactions
 */
export function hasBlockingOverlays(): boolean {
  const overlays = getProblematicOverlays();
  
  return overlays.some(overlay => 
    overlay.display !== 'none' && 
    overlay.opacity !== '0' && 
    overlay.pointerEvents !== 'none'
  );
}

/**
 * Clean up all problematic overlays
 */
export function cleanupOverlays(): number {
  const overlays = getProblematicOverlays();
  let cleaned = 0;

  overlays.forEach(overlay => {
    const { element, display, opacity, pointerEvents } = overlay;
    
    // If overlay is visible but shouldn't be, hide it
    if (display !== 'none' || opacity !== '0' || pointerEvents !== 'none') {
      element.style.display = 'none';
      element.style.pointerEvents = 'none';
      element.style.opacity = '0';
      cleaned++;
      
      console.log('🔧 Cleaned up overlay:', {
        selector: overlay.selector,
        originalStyles: { display, opacity, pointerEvents }
      });
    }
  });

  return cleaned;
}

/**
 * Get elements at a specific point (useful for debugging click interception)
 */
export function getElementsAtPoint(x: number, y: number): Element[] {
  return Array.from(document.elementsFromPoint(x, y));
}

/**
 * Check if a specific element can receive clicks
 */
export function canElementReceiveClicks(element: HTMLElement): boolean {
  const computedStyle = window.getComputedStyle(element);
  
  return (
    computedStyle.display !== 'none' &&
    computedStyle.visibility !== 'hidden' &&
    computedStyle.pointerEvents !== 'none' &&
    computedStyle.opacity !== '0'
  );
}

/**
 * Debug overlay issues by logging current state
 */
export function debugOverlays(): void {
  console.group('🔍 Overlay Debug Information');
  
  const overlays = getProblematicOverlays();
  console.log(`Found ${overlays.length} potential overlay elements`);
  
  overlays.forEach((overlay, index) => {
    console.log(`${index + 1}. ${overlay.selector}:`, {
      zIndex: overlay.zIndex,
      opacity: overlay.opacity,
      display: overlay.display,
      pointerEvents: overlay.pointerEvents,
      position: overlay.position,
    });
  });
  
  const blocking = hasBlockingOverlays();
  console.log(`Has blocking overlays: ${blocking}`);
  
  if (blocking) {
    console.warn('⚠️ Found potentially blocking overlays!');
  }
  
  console.groupEnd();
}

/**
 * Add emergency escape handlers for overlay issues
 */
export function addEmergencyEscapeHandlers(): () => void {
  const handleKeyDown = (event: KeyboardEvent) => {
    // Ctrl+Shift+F12 for emergency overlay cleanup
    if (event.ctrlKey && event.shiftKey && event.key === 'F12') {
      event.preventDefault();
      console.log('🚨 Emergency overlay cleanup triggered');
      const cleaned = cleanupOverlays();
      console.log(`🔧 Cleaned up ${cleaned} overlays`);
    }
    
    // Ctrl+Shift+F11 for overlay debugging
    if (event.ctrlKey && event.shiftKey && event.key === 'F11') {
      event.preventDefault();
      debugOverlays();
    }
  };

  const handleClick = (event: MouseEvent) => {
    // Check for click interception on every click
    const target = event.target as HTMLElement;
    const elementAtPoint = document.elementFromPoint(event.clientX, event.clientY);
    
    if (elementAtPoint !== target) {
      console.warn('🚨 Click intercepted! Target vs element at point:', {
        target: target.tagName + (target.id ? `#${target.id}` : '') + (target.className ? `.${target.className}` : ''),
        elementAtPoint: elementAtPoint?.tagName + (elementAtPoint?.id ? `#${elementAtPoint.id}` : ''),
        elementsAtPoint: getElementsAtPoint(event.clientX, event.clientY).map(el => 
          el.tagName + (el.id ? `#${el.id}` : '') + (el.className ? `.${el.className}` : '')
        )
      });
    }
  };

  document.addEventListener('keydown', handleKeyDown);
  document.addEventListener('click', handleClick, true);

  return () => {
    document.removeEventListener('keydown', handleKeyDown);
    document.removeEventListener('click', handleClick, true);
  };
}
