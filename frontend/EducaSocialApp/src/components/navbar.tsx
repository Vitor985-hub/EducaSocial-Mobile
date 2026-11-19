import { Animated, View } from 'react-native';
import { PlatformPressable } from '@react-navigation/elements';
import { useLinkBuilder } from '@react-navigation/native';
import type { MaterialTopTabBarProps } from '@react-navigation/material-top-tabs';
import Constants from 'expo-constants';
import { theme } from '@/styles/theme';

const statusBarHeight = Constants.statusBarHeight;

export function Navbar({ state, descriptors, navigation, position }: MaterialTopTabBarProps) {
  const { buildHref } = useLinkBuilder();

  return (
    <View
      className="w-full flex-row items-center justify-between border-b-2 px-4 pb-5"
      style={{
        backgroundColor: theme.colors.background,
        borderColor: theme.colors.border,
        marginTop: statusBarHeight + 8,
      }}
    >
      {state.routes.map((route, index) => {
        const { options } = descriptors[route.key];
        const label =
          typeof options.tabBarLabel === 'string'
            ? options.tabBarLabel
            : typeof options.title === 'string'
              ? options.title
              : route.name;
        const isFocused = state.index === index;
        const inputRange = state.routes.map((_, routeIndex) => routeIndex);
        const opacity = position.interpolate({
          inputRange,
          outputRange: inputRange.map((routeIndex) => (routeIndex === index ? 1 : 0.5)),
        });

        const onPress = () => {
          const event = navigation.emit({
            type: 'tabPress',
            target: route.key,
            canPreventDefault: true,
          });

          if (!isFocused && !event.defaultPrevented) {
            navigation.navigate(route.name, route.params);
          }
        };

        return (
          <PlatformPressable
            key={route.key}
            href={buildHref(route.name, route.params)}
            aria-label={options.tabBarAccessibilityLabel}
            aria-selected={isFocused}
            testID={options.tabBarButtonTestID}
            onPress={onPress}
            onLongPress={() => navigation.emit({ type: 'tabLongPress', target: route.key })}
            style={{
              alignItems: 'center',
              backgroundColor: isFocused ? theme.colors.primary : 'transparent',
              borderColor: theme.colors.primary,
              borderRadius: 9999,
              borderWidth: isFocused ? 0 : 2,
              paddingHorizontal: 12,
              paddingVertical: 8,
            }}
          >
            <Animated.Text
              style={{
                color: isFocused ? theme.colors.onPrimary : theme.colors.textSecondary,
                fontSize: theme.fontSizes.md,
                opacity,
              }}
            >
              {label}
            </Animated.Text>
          </PlatformPressable>
        );
      })}
    </View>
  );
}