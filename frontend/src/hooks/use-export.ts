import { useState, useCallback } from "react";
import { useToast } from "@/hooks/use-toast";

interface ExportState {
  isExporting: boolean;
  selectedStartDate: string | null;
  selectedEndDate: string | null;
}

/**
 * Custom hook for managing export operations
 * Follows single responsibility principle - handles only export state
 */
export const useExport = () => {
  const { toast } = useToast();
  const [state, setState] = useState<ExportState>({
    isExporting: false,
    selectedStartDate: null,
    selectedEndDate: null,
  });

  const setDateRange = useCallback((startDate: string | null, endDate: string | null) => {
    setState((prev) => ({
      ...prev,
      selectedStartDate: startDate,
      selectedEndDate: endDate,
    }));
  }, []);

  const setExporting = useCallback((isExporting: boolean) => {
    setState((prev) => ({
      ...prev,
      isExporting,
    }));
  }, []);

  const handleExportError = useCallback((error: Error) => {
    toast({
      title: "Грешка при експорт",
      description: error.message,
      variant: "destructive",
    });
    setExporting(false);
  }, [toast]);

  const handleExportSuccess = useCallback((type: "print" | "calendar") => {
    const message = type === "print" 
      ? "Седмичният график е отворен за печат"
      : "Календарният файл е изтеглен успешно";
    
    toast({
      title: "Успех",
      description: message,
    });
    setExporting(false);
  }, [toast]);

  return {
    state,
    setDateRange,
    setExporting,
    handleExportError,
    handleExportSuccess,
  };
};
