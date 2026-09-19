"use client";

import { Dialog as DialogPrimitive } from "@base-ui/react/dialog";
import { XIcon } from "lucide-react";

import { cn } from "@/lib/utils";

/**
 * Drawer — the evidence rail when the viewport is too narrow to hold it inline.
 *
 * Built on the dialog primitive rather than shadcn's drawer. The stock drawer
 * is a mobile sheet: swipe gestures, snap points, stacking, an 8px corner
 * radius and a blurred overlay. All of that is wrong here — this is a 380px
 * panel that slides in from the right in 180ms, ease-out, and that is the
 * whole animation.
 *
 * (Class names are not written in these comments: Tailwind scans comments and
 * would emit the utility as dead CSS.)
 */

function Drawer({ ...props }: DialogPrimitive.Root.Props) {
  return <DialogPrimitive.Root data-slot="drawer" {...props} />;
}

function DrawerTrigger({ ...props }: DialogPrimitive.Trigger.Props) {
  return <DialogPrimitive.Trigger data-slot="drawer-trigger" {...props} />;
}

function DrawerClose({ ...props }: DialogPrimitive.Close.Props) {
  return <DialogPrimitive.Close data-slot="drawer-close" {...props} />;
}

function DrawerOverlay({
  className,
  ...props
}: DialogPrimitive.Backdrop.Props) {
  return (
    <DialogPrimitive.Backdrop
      data-slot="drawer-overlay"
      className={cn(
        "fixed inset-0 z-50 bg-ink/20",
        "transition-opacity duration-180 ease-out-quiet",
        "data-starting-style:opacity-0 data-ending-style:opacity-0",
        className,
      )}
      {...props}
    />
  );
}

function DrawerContent({
  className,
  children,
  showCloseButton = true,
  ...props
}: DialogPrimitive.Popup.Props & { showCloseButton?: boolean }) {
  return (
    <DialogPrimitive.Portal>
      <DrawerOverlay />
      <DialogPrimitive.Popup
        data-slot="drawer-content"
        className={cn(
          "fixed inset-y-0 right-0 z-50 flex w-95 max-w-[90vw] flex-col",
          "border-l border-rule-strong bg-panel text-13 text-ink shadow-drawer",
          "transition-transform duration-180 ease-out-quiet outline-none",
          "data-starting-style:translate-x-full data-ending-style:translate-x-full",
          className,
        )}
        {...props}
      >
        {children}
        {showCloseButton && (
          <DialogPrimitive.Close
            data-slot="drawer-close"
            aria-label="Close evidence"
            className={cn(
              "absolute top-3 right-3 inline-flex size-6 items-center justify-center rounded-sm",
              "text-ink-muted transition-colors duration-100",
              "hover:bg-tint-hover hover:text-ink",
            )}
          >
            <XIcon className="size-3.5" strokeWidth={1.5} />
          </DialogPrimitive.Close>
        )}
      </DialogPrimitive.Popup>
    </DialogPrimitive.Portal>
  );
}

function DrawerHeader({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="drawer-header"
      className={cn(
        "flex shrink-0 flex-col gap-1 border-b border-rule px-4 py-3",
        className,
      )}
      {...props}
    />
  );
}

function DrawerBody({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="drawer-body"
      className={cn("min-h-0 flex-1 overflow-y-auto", className)}
      {...props}
    />
  );
}

function DrawerFooter({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="drawer-footer"
      className={cn(
        "flex shrink-0 items-center gap-2 border-t border-rule px-4 py-3",
        className,
      )}
      {...props}
    />
  );
}

function DrawerTitle({ className, ...props }: DialogPrimitive.Title.Props) {
  return (
    <DialogPrimitive.Title
      data-slot="drawer-title"
      className={cn("font-display text-18 text-ink", className)}
      {...props}
    />
  );
}

function DrawerDescription({
  className,
  ...props
}: DialogPrimitive.Description.Props) {
  return (
    <DialogPrimitive.Description
      data-slot="drawer-description"
      className={cn("text-12 text-ink-muted", className)}
      {...props}
    />
  );
}

export {
  Drawer,
  DrawerTrigger,
  DrawerClose,
  DrawerOverlay,
  DrawerContent,
  DrawerHeader,
  DrawerBody,
  DrawerFooter,
  DrawerTitle,
  DrawerDescription,
};
