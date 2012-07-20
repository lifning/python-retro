cdef extern from "SDL.h" nogil:
	ctypedef unsigned char Uint8
	ctypedef unsigned long Uint32
	ctypedef unsigned long long Uint64
	ctypedef signed long long Sint64
	ctypedef signed short Sint16
	ctypedef unsigned short Uint16


	ctypedef enum:
		SDL_PIXELFORMAT_ARGB8888


	ctypedef enum SDL_BlendMode:
		SDL_BLENDMODE_NONE = 0x00000000
		SDL_BLENDMODE_BLEND = 0x00000001
		SDL_BLENDMODE_ADD = 0x00000002
		SDL_BLENDMODE_MOD = 0x00000004


	ctypedef enum SDL_TextureAccess:
		SDL_TEXTUREACCESS_STATIC
		SDL_TEXTUREACCESS_STREAMING
		SDL_TEXTUREACCESS_TARGET

	ctypedef enum SDL_RendererFlags:
		SDL_RENDERER_SOFTWARE = 0x00000001
		SDL_RENDERER_ACCELERATED = 0x00000002
		SDL_RENDERER_PRESENTVSYNC = 0x00000004
		
	ctypedef enum SDL_bool:
		SDL_FALSE = 0
		SDL_TRUE = 1

	cdef struct SDL_Rect:
		int x, y
		int w, h

	ctypedef struct SDL_Point:
		int x, y

	cdef struct SDL_Color:
		Uint8 r
		Uint8 g
		Uint8 b
		Uint8 unused

	cdef struct SDL_Palette:
		int ncolors
		SDL_Color *colors
		Uint32 version
		int refcount

	cdef struct SDL_PixelFormat:
		Uint32 format
		SDL_Palette *palette
		Uint8 BitsPerPixel
		Uint8 BytesPerPixel
		Uint8 padding[2]
		Uint32 Rmask
		Uint32 Gmask
		Uint32 Bmask
		Uint32 Amask
		Uint8 Rloss
		Uint8 Gloss
		Uint8 Bloss
		Uint8 Aloss
		Uint8 Rshift
		Uint8 Gshift
		Uint8 Bshift
		Uint8 Ashift
		int refcount
		SDL_PixelFormat *next


	cdef struct SDL_BlitMap

	cdef struct SDL_Surface:
		Uint32 flags
		SDL_PixelFormat *format
		int w, h
		int pitch
		void *pixels
		void *userdata
		int locked
		void *lock_data
		SDL_Rect clip_rect
		SDL_BlitMap *map
		int refcount

	cdef enum:
		SDL_INIT_TIMER       = 0x00000001
		SDL_INIT_AUDIO       = 0x00000010
		SDL_INIT_VIDEO       = 0x00000020
		SDL_INIT_CDROM       = 0x00000100
		SDL_INIT_JOYSTICK    = 0x00000200
		SDL_INIT_NOPARACHUTE = 0x00100000
		SDL_INIT_EVENTTHREAD = 0x01000000
		SDL_INIT_EVERYTHING  = 0x0000FFFF

	ctypedef enum SDL_EventType:
		SDL_FIRSTEVENT	 = 0,
		SDL_QUIT		   = 0x100
		SDL_WINDOWEVENT	= 0x200
		SDL_SYSWMEVENT
		SDL_KEYDOWN		= 0x300
		SDL_KEYUP
		SDL_TEXTEDITING
		SDL_TEXTINPUT
		SDL_MOUSEMOTION	= 0x400
		SDL_MOUSEBUTTONDOWN
		SDL_MOUSEBUTTONUP
		SDL_MOUSEWHEEL
		SDL_INPUTMOTION	= 0x500
		SDL_INPUTBUTTONDOWN
		SDL_INPUTBUTTONUP
		SDL_INPUTWHEEL
		SDL_INPUTPROXIMITYIN
		SDL_INPUTPROXIMITYOUT
		SDL_JOYAXISMOTION  = 0x600
		SDL_JOYBALLMOTION
		SDL_JOYHATMOTION
		SDL_JOYBUTTONDOWN
		SDL_JOYBUTTONUP
		SDL_FINGERDOWN	  = 0x700
		SDL_FINGERUP
		SDL_FINGERMOTION
		SDL_TOUCHBUTTONDOWN
		SDL_TOUCHBUTTONUP
		SDL_DOLLARGESTURE   = 0x800
		SDL_DOLLARRECORD
		SDL_MULTIGESTURE
		SDL_CLIPBOARDUPDATE = 0x900
		SDL_EVENT_COMPAT1 = 0x7000
		SDL_EVENT_COMPAT2
		SDL_EVENT_COMPAT3
		SDL_USEREVENT	= 0x8000
		SDL_LASTEVENT	= 0xFFFF

	ctypedef enum SDL_WindowEventID:
		SDL_WINDOWEVENT_NONE		   #< Never used */
		SDL_WINDOWEVENT_SHOWN		  #< Window has been shown */
		SDL_WINDOWEVENT_HIDDEN		 #< Window has been hidden */
		SDL_WINDOWEVENT_EXPOSED		#< Window has been exposed and should be
										#	 redrawn */
		SDL_WINDOWEVENT_MOVED		  #< Window has been moved to data1, data2
										# */
		SDL_WINDOWEVENT_RESIZED		#< Window has been resized to data1xdata2 */
		SDL_WINDOWEVENT_SIZE_CHANGED   #< The window size has changed, either as a result of an API call or through the system or user changing the window size. */
		SDL_WINDOWEVENT_MINIMIZED	  #< Window has been minimized */
		SDL_WINDOWEVENT_MAXIMIZED	  #< Window has been maximized */
		SDL_WINDOWEVENT_RESTORED	   #< Window has been restored to normal size
										# and position */
		SDL_WINDOWEVENT_ENTER		  #< Window has gained mouse focus */
		SDL_WINDOWEVENT_LEAVE		  #< Window has lost mouse focus */
		SDL_WINDOWEVENT_FOCUS_GAINED   #< Window has gained keyboard focus */
		SDL_WINDOWEVENT_FOCUS_LOST	 #< Window has lost keyboard focus */
		SDL_WINDOWEVENT_CLOSE		   #< The window manager requests that the
										# window be closed */

	ctypedef enum SDL_WindowFlags:
		SDL_WINDOW_FULLSCREEN = 0x00000001
		SDL_WINDOW_OPENGL = 0x00000002
		SDL_WINDOW_SHOWN = 0x00000004
		SDL_WINDOW_HIDDEN = 0x00000008
		SDL_WINDOW_BORDERLESS = 0x00000010
		SDL_WINDOW_RESIZABLE = 0x00000020
		SDL_WINDOW_MINIMIZED = 0x00000040
		SDL_WINDOW_MAXIMIZED = 0x00000080
		SDL_WINDOW_INPUT_GRABBED = 0x00000100
		SDL_WINDOW_INPUT_FOCUS = 0x00000200
		SDL_WINDOW_MOUSE_FOCUS = 0x00000400
		SDL_WINDOW_FOREIGN = 0x00000800

	ctypedef enum SDL_RendererFlip:
		SDL_FLIP_NONE = 0x00000000
		SDL_FLIP_HORIZONTAL = 0x00000001
		SDL_FLIP_VERTICAL = 0x00000002

	cdef enum:
		SDL_HAT_CENTERED  = 0x00
		SDL_HAT_UP		= 0x01
		SDL_HAT_RIGHT	 = 0x02
		SDL_HAT_DOWN	  = 0x04
		SDL_HAT_LEFT	  = 0x08
		SDL_HAT_RIGHTUP   = (SDL_HAT_RIGHT|SDL_HAT_UP)
		SDL_HAT_RIGHTDOWN = (SDL_HAT_RIGHT|SDL_HAT_DOWN)
		SDL_HAT_LEFTUP	= (SDL_HAT_LEFT|SDL_HAT_UP)
		SDL_HAT_LEFTDOWN  = (SDL_HAT_LEFT|SDL_HAT_DOWN)

	cdef struct SDL_MouseMotionEvent:
		Uint32 type
		Uint32 windowID
		Uint8 state
		Uint8 padding1
		Uint8 padding2
		Uint8 padding3
		int x
		int y
		int xrel
		int yrel

	cdef struct SDL_MouseButtonEvent:
		Uint32 type
		Uint32 windowID
		Uint8 button
		Uint8 state
		Uint8 padding1
		Uint8 padding2
		int x
		int y

	cdef struct SDL_WindowEvent:
		Uint32 type
		Uint32 windowID
		Uint8 event
		Uint8 padding1
		Uint8 padding2
		Uint8 padding3
		int data1
		int data2

	ctypedef Sint64 SDL_TouchID
	ctypedef Sint64 SDL_FingerID

	cdef struct SDL_TouchFingerEvent:
		Uint32 type
		Uint32 windowID
		SDL_TouchID touchId
		SDL_FingerID fingerId
		Uint8 state
		Uint8 padding1
		Uint8 padding2
		Uint8 padding3
		Uint16 x
		Uint16 y
		Sint16 dx
		Sint16 dy
		Uint16 pressure



	cdef struct SDL_KeyboardEvent:
		pass
	cdef struct SDL_TextEditingEvent:
		pass
	cdef struct SDL_TextInputEvent:
		pass
	cdef struct SDL_MouseWheelEvent:
		Uint32 type
		Uint32 windowID
		int x
		int y
		
	cdef struct SDL_JoyAxisEvent:
		pass
	cdef struct SDL_JoyBallEvent:
		pass
	cdef struct SDL_JoyHatEvent:
		pass
	cdef struct SDL_JoyButtonEvent:
		pass
	cdef struct SDL_QuitEvent:
		pass
	cdef struct SDL_UserEvent:
		pass
	cdef struct SDL_SysWMEvent:
		pass
	cdef struct SDL_TouchFingerEvent:
		pass
	cdef struct SDL_TouchButtonEvent:
		pass
	cdef struct SDL_MultiGestureEvent:
		pass
	cdef struct SDL_DollarGestureEvent:
		pass

	cdef union SDL_Event:
		Uint32 type
		SDL_WindowEvent window
		SDL_KeyboardEvent key
		SDL_TextEditingEvent edit
		SDL_TextInputEvent text
		SDL_MouseMotionEvent motion
		SDL_MouseButtonEvent button
		SDL_MouseWheelEvent wheel
		SDL_JoyAxisEvent jaxis
		SDL_JoyBallEvent jball
		SDL_JoyHatEvent jhat
		SDL_JoyButtonEvent jbutton
		SDL_QuitEvent quit
		SDL_UserEvent user
		SDL_SysWMEvent syswm
		SDL_TouchFingerEvent tfinger
		SDL_TouchButtonEvent tbutton
		SDL_MultiGestureEvent mgesture
		SDL_DollarGestureEvent dgesture

	cdef struct SDL_RendererInfo:
		char *name
		Uint32 flags
		Uint32 num_texture_formats
		Uint32 texture_formats[16]
		int max_texture_width
		int max_texture_height

	ctypedef struct SDL_Texture
	ctypedef struct SDL_Renderer
	ctypedef struct SDL_Window
	ctypedef struct SDL_DisplayMode:
		Uint32 format
		int w
		int h
		int refresh_rate
		void *driverdata


	cdef struct SDL_RWops:
		long (* seek) (SDL_RWops * context, long offset,int whence)
		size_t(* read) ( SDL_RWops * context, void *ptr, size_t size, size_t maxnum)
		size_t(* write) (SDL_RWops * context, void *ptr,size_t size, size_t num)
		int (* close) (SDL_RWops * context)

	cdef SDL_Renderer * SDL_CreateRenderer(SDL_Window * window, int index, Uint32 flags)	
	cdef SDL_Texture * SDL_CreateTexture(SDL_Renderer * renderer, Uint32 format, int access, int w, int h)
	cdef SDL_Texture * SDL_CreateTextureFromSurface(SDL_Renderer * renderer, SDL_Surface * surface)
	cdef SDL_Surface * SDL_CreateRGBSurface(Uint32 flags, int width, int height, int depth, Uint32 Rmask, Uint32 Gmask, Uint32 Bmask, Uint32 Amask)
	cdef int SDL_RenderCopy(SDL_Renderer * renderer, SDL_Texture * texture, SDL_Rect * srcrect, SDL_Rect * dstrect)
	cdef void SDL_RenderPresent(SDL_Renderer * renderer)
	cdef int SDL_SetTargetTexture(SDL_Texture *texture)
	cdef void SDL_DestroyTexture(SDL_Texture * texture)
	cdef void SDL_FreeSurface(SDL_Surface * surface)
	cdef int SDL_BlitSurface(SDL_Surface *src, SDL_Rect *srcrect, SDL_Surface *dst, SDL_Rect *dstrect)
	cdef int SDL_UpperBlit (SDL_Surface * src, SDL_Rect * srcrect, SDL_Surface * dst, SDL_Rect * dstrect)
	cdef int SDL_LockTexture(SDL_Texture * texture, SDL_Rect * rect, void **pixels, int *pitch)
	cdef void SDL_UnlockTexture(SDL_Texture * texture)
	cdef void SDL_GetWindowSize(SDL_Window * window, int *w, int *h)
	cdef SDL_Window * SDL_CreateWindow(char *title, int x, int y, int w, int h, Uint32 flags)
	cdef int SDL_SetRenderDrawColor(SDL_Renderer * renderer, Uint8 r, Uint8 g, Uint8 b, Uint8 a)
	cdef int SDL_RenderClear(SDL_Renderer * renderer)
	cdef SDL_Surface * SDL_CreateRGBSurfaceFrom(void *pixels, int width, int height, int depth, int pitch, Uint32 Rmask, Uint32 Gmask, Uint32 Bmask, Uint32 Amask)
	cdef int SDL_Init(Uint32 flags)
	cdef void SDL_Quit()
	cdef int SDL_EnableUNICODE(int enable)
	cdef Uint32 SDL_GetTicks()
	cdef void SDL_Delay(Uint32 ms)
	cdef int SDL_PollEvent(SDL_Event * event)
	cdef SDL_RWops * SDL_RWFromFile(char *file, char *mode)
	cdef void SDL_FreeRW(SDL_RWops *area)
	cdef int SDL_GetRendererInfo(SDL_Renderer *renderer, SDL_RendererInfo *info)
	cdef int SDL_RenderSetViewport(SDL_Renderer * renderer, SDL_Rect * rect)
	cdef int SDL_GetCurrentDisplayMode(int displayIndex, SDL_DisplayMode * mode)
	cdef int SDL_GetDesktopDisplayMode(int displayIndex, SDL_DisplayMode * mode)	
	cdef int SDL_SetTextureColorMod(SDL_Texture * texture, Uint8 r, Uint8 g, Uint8 b)
	cdef int SDL_SetTextureAlphaMod(SDL_Texture * texture, Uint8 alpha)
	cdef char * SDL_GetError()
	cdef int SDL_Flip(SDL_Surface* screen)
	cdef void SDL_WM_SetCaption(char *title, char *icon)

cdef extern from "SDL_joystick.h" nogil:
	ctypedef struct SDL_Joystick
	cdef void SDL_JoystickUpdate()
	cdef SDL_Joystick* SDL_JoystickOpen(int index)
	cdef Sint16 SDL_JoystickGetAxis(SDL_Joystick *joystick, int axis)
	cdef Uint8 SDL_JoystickGetButton(SDL_Joystick *joystick, int button)
	cdef Uint8 SDL_JoystickGetHat(SDL_Joystick *joystick, int hat)
	cdef int SDL_JoystickNumAxes(SDL_Joystick *joystick)
	cdef int SDL_JoystickNumButtons(SDL_Joystick *joystick)
	cdef int SDL_JoystickNumHats(SDL_Joystick *joystick)

cdef extern from "SDL_mixer.h" nogil:
	ctypedef struct Mix_Chunk:
		int allocated
		Uint8 *abuf
		Uint32 alen
		Uint8 volume

	cdef Mix_Chunk* Mix_QuickLoad_RAW(Uint8 *mem, Uint32 len)
	cdef int Mix_PlayChannel(int channel, Mix_Chunk *chunk, int loops)
	cdef void Mix_FreeChunk(Mix_Chunk *chunk)
	cdef void Mix_Pause(int channel)
	cdef void Mix_Resume(int channel)

