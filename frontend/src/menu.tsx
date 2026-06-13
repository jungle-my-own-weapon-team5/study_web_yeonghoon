import {
  NavigationMenu,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  navigationMenuTriggerStyle,
} from "@/components/ui/navigation-menu"

type MenuProps = {
  isLogin:boolean

}

export function NavigationMenuDemo({isLogin}:MenuProps) {
  const menuJSON = [
    {
      titleKey: "Board" as const,
      descriptionKey: "board page" as const,
      href: "/test",
    },
    {
      titleKey: isLogin?"MyPage":"Login" as const,
      descriptionKey: isLogin?"my page":"login page" as const,
      href: isLogin?"/t":"/",
    },
  ]
  return (
    <NavigationMenu>
      <NavigationMenuList>
        {
            menuJSON.map((menu)=>(
            <NavigationMenuItem key={menu.titleKey}>
              <NavigationMenuLink asChild>
                <a href={menu.href} className={navigationMenuTriggerStyle()}>
                  {menu.titleKey}
                </a>
              </NavigationMenuLink>
            </NavigationMenuItem>
            )
          )
        }
      </NavigationMenuList>
    </NavigationMenu>
  )
}
