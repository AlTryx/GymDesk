import { useState } from "react";
import { format } from "date-fns";
import { enUS } from "date-fns/locale";
import { Calendar, Download, Printer, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import {
  Calendar as CalendarComponent,
} from "@/components/ui/calendar";
import { useExport } from "@/hooks/use-export";
import { exportApi } from "@/api/client";

/**
 * Export controls component for weekly schedule printing and calendar export
 * Implements single responsibility principle - handles only UI for exports
 */
export const ExportControls = () => {
  const { state, setDateRange, setExporting, handleExportError, handleExportSuccess } = useExport();
  const [startDate, setStartDate] = useState<Date | undefined>(
    new Date(new Date().setDate(new Date().getDate() - 7))
  );
  const [endDate, setEndDate] = useState<Date | undefined>(
    new Date(new Date().setDate(new Date().getDate() + 7))
  );
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  const validateDateRange = (): boolean => {
    if (!startDate || !endDate) {
      handleExportError(new Error("Моля, изберете начална и крайна дата"));
      return false;
    }
    if (startDate > endDate) {
      handleExportError(new Error("Начална дата не може да е след крайната дата"));
      return false;
    }
    return true;
  };

  const handleExportPrint = async () => {
    if (!validateDateRange()) return;

    setExporting(true);
    try {
      const startStr = format(startDate!, "yyyy-MM-dd");
      const endStr = format(endDate!, "yyyy-MM-dd");

      await exportApi.weeklySchedulePrint(startStr, endStr);
      handleExportSuccess("print");
      setIsDialogOpen(false);
    } catch (error) {
      handleExportError(error instanceof Error ? error : new Error("Unknown error"));
    }
  };

  const handleExportCalendar = async () => {
    if (!validateDateRange()) return;

    setExporting(true);
    try {
      const startStr = format(startDate!, "yyyy-MM-dd");
      const endStr = format(endDate!, "yyyy-MM-dd");

      await exportApi.calendarIcs(startStr, endStr);
      handleExportSuccess("calendar");
      setIsDialogOpen(false);
    } catch (error) {
      handleExportError(error instanceof Error ? error : new Error("Unknown error"));
    }
  };

  return (
    <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm" className="gap-2">
          <Download className="w-4 h-4" />
          Експорт
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Експорт на резервации</DialogTitle>
          <DialogDescription>
            Изберете период и формат за експорт на вашите резервации
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Start Date */}
          <div className="space-y-2">
            <Label htmlFor="start-date">Начална дата</Label>
            <Popover>
              <PopoverTrigger asChild>
                <Button
                  id="start-date"
                  variant="outline"
                  className="w-full justify-start text-left font-normal"
                >
                  <Calendar className="mr-2 h-4 w-4" />
                  {startDate ? format(startDate, "dd MMM yyyy", { locale: enUS }) : "Изберете дата"}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0" align="start">
                <CalendarComponent
                  mode="single"
                  selected={startDate}
                  onSelect={setStartDate}
                  disabled={(date) => endDate ? date > endDate : false}
                />
              </PopoverContent>
            </Popover>
          </div>

          {/* End Date */}
          <div className="space-y-2">
            <Label htmlFor="end-date">Крайна дата</Label>
            <Popover>
              <PopoverTrigger asChild>
                <Button
                  id="end-date"
                  variant="outline"
                  className="w-full justify-start text-left font-normal"
                >
                  <Calendar className="mr-2 h-4 w-4" />
                  {endDate ? format(endDate, "dd MMM yyyy", { locale: enUS }) : "Изберете дата"}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0" align="start">
                <CalendarComponent
                  mode="single"
                  selected={endDate}
                  onSelect={setEndDate}
                  disabled={(date) => startDate ? date < startDate : false}
                />
              </PopoverContent>
            </Popover>
          </div>

          {/* Format Selection */}
          <div className="pt-2">
            <Label className="text-sm font-semibold mb-3 block">Формат на експорт</Label>
            <div className="space-y-2">
              <Button
                onClick={handleExportPrint}
                disabled={state.isExporting}
                className="w-full justify-start gap-2"
                variant="secondary"
              >
                {state.isExporting ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Printer className="w-4 h-4" />
                )}
                Печат на график (HTML)
              </Button>
              <Button
                onClick={handleExportCalendar}
                disabled={state.isExporting}
                className="w-full justify-start gap-2"
                variant="secondary"
              >
                {state.isExporting ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Download className="w-4 h-4" />
                )}
                Календарен файл (.ics)
              </Button>
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button type="button" variant="outline" onClick={() => setIsDialogOpen(false)}>
            Затвори
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
