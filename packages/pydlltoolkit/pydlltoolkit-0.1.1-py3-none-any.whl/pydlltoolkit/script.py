import win32api
import win32con
import win32event
import win32process
import os

__all__ = ["DllInjector"]


class DllInjector:

    def inject(self, pid: int, dll_path: str) -> bool:
        dll_name = os.path.basename(dll_path)

        if self.is_dll_injected(pid, dll_name):
            print("[-] DLL is already injected.")
            return False

        print(f"[+] Injecting into PID {pid}: {dll_path}")

        h_process = None
        thread_handle = None

        try:
            dll_bytes = os.path.abspath(dll_path).encode("ascii")
            size = len(dll_bytes) + 1

            h_process = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, False, pid)
            if not h_process:
                print("[-] OpenProcess failed")
                return False

            arg_address = win32process.VirtualAllocEx(
                h_process, 0, size, win32con.MEM_COMMIT, win32con.PAGE_READWRITE
            )

            if not arg_address:
                print("[-] Cannot allocate memory in target process")
                return False

            write_memory = win32process.WriteProcessMemory(
                h_process,
                arg_address,
                dll_bytes,
            )

            if not write_memory:
                print("[-] Failed to write DLL path")
                return False

            h_kernel32 = win32api.GetModuleHandle("kernel32.dll")
            h_loadlib = win32api.GetProcAddress(h_kernel32, "LoadLibraryA")

            if not h_loadlib:
                print("[-] Failed to get address of LoadLibraryA")
                return False

            thread_handle, thread_id = win32process.CreateRemoteThread(
                h_process, None, 0, h_loadlib, arg_address, 0
            )

            if not thread_handle:
                print("[-] Failed to create remote thread in target process")
                return False

            thread_wait = win32event.WaitForSingleObject(thread_handle, 5000)

            if thread_wait == win32con.WAIT_TIMEOUT:
                print("[-] Warning: Remote thread timed out")
                return False

            print(f"[+] DLL injected. Thread ID: {thread_id}")
            return True
        except Exception as e:
            print(f"[-] Exception during injection: {e}")
            return False
        finally:
            if thread_handle:
                win32api.CloseHandle(thread_handle)
            if h_process:
                win32api.CloseHandle(h_process)

    def uninject(self, pid: int, dll_name: str) -> bool:
        print(f"[+] Attempting to unload DLL: {dll_name} from PID {pid}")

        h_process = None
        thread_handle = None

        try:
            h_process = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, False, pid)
            if not h_process:
                print("[-] OpenProcess failed")
                return False

            modules = win32process.EnumProcessModulesEx(h_process, 0x03)

            if not modules:
                print("[-] Failed to enumerate modules")
                return False

            target_module = None

            for mod in modules:
                full_path = win32process.GetModuleFileNameEx(h_process, mod)
                base_name = str(os.path.basename(full_path))

                if base_name.lower() == dll_name.lower():
                    target_module = mod
                    break

            if not target_module:
                print("[-] DLL not found in process")
                return False

            h_kernel32 = win32api.GetModuleHandle("kernel32.dll")
            h_free_lib = win32api.GetProcAddress(h_kernel32, "FreeLibrary")

            thread_handle, thread_id = win32process.CreateRemoteThread(
                h_process, None, 0, h_free_lib, target_module, 0
            )

            if not thread_handle:
                print("[-] Failed to create remote thread for FreeLibrary")
                return False

            thread_wait = win32event.WaitForSingleObject(thread_handle, 5000)

            if thread_wait == win32con.WAIT_TIMEOUT:
                print("[-] Warning: Remote thread timed out")
                return False

            print(f"[+] DLL unloaded. Thread ID: {thread_id}")
            return True
        except Exception as e:
            print(f"[-] Exception during uninject: {e}")
            return False
        finally:
            if thread_handle:
                win32api.CloseHandle(thread_handle)
            if h_process:
                win32api.CloseHandle(h_process)

    def is_dll_injected(self, pid: int, dll_name: str) -> bool:
        h_process = None
        try:
            h_process = win32api.OpenProcess(
                win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ,
                False,
                pid,
            )

            modules = win32process.EnumProcessModulesEx(h_process, 0x03)

            for mod in modules:
                full_path = win32process.GetModuleFileNameEx(h_process, mod)
                base_name = str(os.path.basename(full_path))
                if base_name.lower() == dll_name.lower():
                    return True
            return False

        except Exception as e:
            print(f"[-] Error checking DLL injection in PID {pid}: {e}")
            return False
        finally:
            if h_process:
                win32api.CloseHandle(h_process)
