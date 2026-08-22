import { ExpandableTabs } from "./ui/expandable-tabs";

export function ExpandableTabsDemo() {
  const defaultTabs = [
    { title: "Dashboard", icon: "bi-house-door" },
    { title: "Notifications", icon: "bi-bell" },
    { type: "separator" },
    { title: "Settings", icon: "bi-gear" },
    { title: "Support", icon: "bi-question-circle" },
    { title: "Security", icon: "bi-shield-check" },
  ] as any[];

  const customColorTabs = [
    { title: "Profile", icon: "bi-person" },
    { title: "Messages", icon: "bi-envelope" },
    { type: "separator" },
    { title: "Documents", icon: "bi-file-earmark-text" },
    { title: "Privacy", icon: "bi-lock" },
  ] as any[];

  return (
    <div className="flex flex-col gap-4 p-4 items-center justify-start min-h-fit">
      <div className="text-sm text-muted-foreground mb-4 md:hidden">Mobile View (Tabs are visible below)</div>
      <div className="text-sm text-muted-foreground mb-4 hidden md:block">Desktop View (Tabs are hidden on this breakpoint)</div>
      <ExpandableTabs tabs={defaultTabs} />
      <ExpandableTabs
        tabs={customColorTabs}
        activeColor="text-blue-500"
        className="border-blue-200 dark:border-blue-800"
      />
    </div>
  );
}
