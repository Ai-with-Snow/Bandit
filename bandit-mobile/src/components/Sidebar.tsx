
import React from 'react';
import { View, Text, ScrollView, TouchableOpacity, StyleSheet, TextInput } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { theme } from '../constants/theme';
import { Project, Conversation } from '../lib/api';
import { BlurView } from 'expo-blur';

interface SidebarProps {
    conversations: Conversation[];
    projects: Project[];
    currentId: string | null;
    onSelect: (id: string) => void;
    onNewChat: () => void;
    onCreateProject: (name: string, options?: { description?: string, color?: string, icon?: string }) => void;
    onRenameProject: (projectId: string, newName: string) => void;
    onRenameConversation: (id: string, newTitle: string) => void;
    onDeleteConversation: (id: string) => void;
    onDeleteProject: (projectId: string) => void;
    onUpdateProject: (projectId: string, updates: any) => void;
    onAssignProject: (convId: string, projId: string) => void;
    onClose: () => void;
    onOpenSettings: () => void;
    // Collapse state props (lifted from parent for persistence)
    projectsExpanded: boolean;
    setProjectsExpanded: (expanded: boolean) => void;
    chatsExpanded: boolean;
    setChatsExpanded: (expanded: boolean) => void;
}

export function Sidebar({ conversations, projects, currentId, onSelect, onNewChat, onCreateProject, onRenameProject, onDeleteProject, onUpdateProject, onClose, onOpenSettings, projectsExpanded, setProjectsExpanded, chatsExpanded, setChatsExpanded }: SidebarProps) {
    const [projectModal, setProjectModal] = React.useState<{ visible: boolean, mode: 'create' | 'edit', projectId?: string, name: string, color?: string, icon?: string }>({
        visible: false, mode: 'create', name: '', color: undefined, icon: undefined
    });
    const [projectMenu, setProjectMenu] = React.useState<{ visible: boolean, projectId: string | null }>({
        visible: false, projectId: null
    });

    // Color palette for projects
    const colorPalette = ['#E0D7FE', '#FFD6E0', '#D4EDDA', '#D6E9FF', '#FFF3CD', '#F5D0C5', '#D4F4FA', '#E8E8E8'];
    // Icon options for projects
    const iconOptions = ['folder-outline', 'briefcase-outline', 'code-slash-outline', 'book-outline', 'heart-outline', 'star-outline', 'rocket-outline', 'bulb-outline'];

    const handleCreateProjectPress = () => {
        setProjectModal({ visible: true, mode: 'create', name: '', color: undefined, icon: undefined });
    };

    const handleEditProject = (proj: typeof projects[0]) => {
        setProjectMenu({ visible: false, projectId: null });
        setProjectModal({ visible: true, mode: 'edit', projectId: proj.id, name: proj.name, color: proj.color, icon: proj.icon });
    };

    const handleDeleteProject = (projectId: string) => {
        setProjectMenu({ visible: false, projectId: null });
        onDeleteProject(projectId);
    };

    const saveProject = () => {
        if (!projectModal.name.trim()) return;
        if (projectModal.mode === 'create') {
            onCreateProject(projectModal.name, { color: projectModal.color, icon: projectModal.icon });
        } else if (projectModal.mode === 'edit' && projectModal.projectId) {
            onUpdateProject(projectModal.projectId, { name: projectModal.name, color: projectModal.color, icon: projectModal.icon });
        }
        setProjectModal({ ...projectModal, visible: false });
    };

    return (
        <View style={styles.container}>
            {/* Top Section - Hamburger + New Chat */}
            <View style={styles.topSection}>
                <TouchableOpacity style={styles.hamburgerButton} onPress={onClose}>
                    <Ionicons name="menu" size={22} color="#3D3D3D" />
                </TouchableOpacity>

                <TouchableOpacity style={styles.newChatButton} onPress={onNewChat}>
                    <Ionicons name="create-outline" size={18} color="#3D3D3D" />
                    <Text style={styles.newChatText}>New chat</Text>
                </TouchableOpacity>
            </View>

            {/* Scrollable Content - with bottom padding for footer space */}
            <ScrollView style={styles.scrollContent} contentContainerStyle={{ paddingBottom: 80 }} showsVerticalScrollIndicator={false}>

                {/* Projects Section - Collapsible */}
                <View style={styles.section}>
                    <TouchableOpacity
                        style={styles.sectionHeader}
                        onPress={() => setProjectsExpanded(!projectsExpanded)}
                    >
                        <Text style={styles.sectionTitle}>Projects</Text>
                        <Ionicons
                            name={projectsExpanded ? "chevron-down" : "chevron-forward"}
                            size={16}
                            color="#5E5E5E"
                        />
                    </TouchableOpacity>

                    {projectsExpanded && (
                        <>
                            {/* New Project Button */}
                            <TouchableOpacity style={styles.navItem} onPress={handleCreateProjectPress}>
                                <Ionicons name="add-circle-outline" size={18} color="#5E5E5E" />
                                <Text style={styles.navItemText}>New project</Text>
                            </TouchableOpacity>

                            {/* Project List */}
                            {projects.map(proj => (
                                <View key={proj.id} style={styles.projectRow}>
                                    <TouchableOpacity
                                        style={[styles.navItem, { flex: 1 }, currentId === proj.id && styles.navItemActive]}
                                        onPress={() => onSelect(proj.id)}
                                    >
                                        <View style={[styles.projectIcon, proj.color ? { backgroundColor: proj.color } : {}]}>
                                            <Ionicons name={(proj.icon as any) || "folder-outline"} size={14} color="#3D3D3D" />
                                        </View>
                                        <Text style={styles.navItemText} numberOfLines={1}>{proj.name}</Text>
                                    </TouchableOpacity>
                                    <TouchableOpacity
                                        style={styles.ellipsisButton}
                                        onPress={() => setProjectMenu({ visible: true, projectId: proj.id })}
                                    >
                                        <Ionicons name="ellipsis-horizontal" size={16} color="#9CA3AF" />
                                    </TouchableOpacity>

                                    {/* Project Options Menu */}
                                    {projectMenu.visible && projectMenu.projectId === proj.id && (
                                        <View style={styles.projectOptionsMenu}>
                                            <TouchableOpacity style={styles.menuItem} onPress={() => handleEditProject(proj)}>
                                                <Ionicons name="pencil-outline" size={16} color="#3D3D3D" />
                                                <Text style={styles.menuItemText}>Rename / Edit</Text>
                                            </TouchableOpacity>
                                            <TouchableOpacity style={styles.menuItem} onPress={() => handleDeleteProject(proj.id)}>
                                                <Ionicons name="trash-outline" size={16} color="#EF4444" />
                                                <Text style={[styles.menuItemText, { color: '#EF4444' }]}>Delete</Text>
                                            </TouchableOpacity>
                                        </View>
                                    )}
                                </View>
                            ))}
                        </>
                    )}
                </View>

                {/* Your Chats Section - Collapsible */}
                <View style={styles.section}>
                    <TouchableOpacity
                        style={styles.sectionHeader}
                        onPress={() => setChatsExpanded(!chatsExpanded)}
                    >
                        <Text style={styles.sectionTitle}>Your chats</Text>
                        <Ionicons
                            name={chatsExpanded ? "chevron-down" : "chevron-forward"}
                            size={16}
                            color="#5E5E5E"
                        />
                    </TouchableOpacity>

                    {chatsExpanded && (
                        <>
                            {/* New Chat Button */}
                            <TouchableOpacity style={styles.navItem} onPress={onNewChat}>
                                <Ionicons name="add-circle-outline" size={18} color="#5E5E5E" />
                                <Text style={styles.navItemText}>New chat</Text>
                            </TouchableOpacity>

                            {/* Chat List - Simple text items */}
                            {conversations.map(conv => (
                                <TouchableOpacity
                                    key={conv.id}
                                    style={[styles.chatItem, currentId === conv.id && styles.chatItemActive]}
                                    onPress={() => onSelect(conv.id)}
                                >
                                    <Text style={styles.chatItemText} numberOfLines={1}>{conv.title}</Text>
                                </TouchableOpacity>
                            ))}

                            {conversations.length === 0 && (
                                <Text style={styles.emptyText}>No chats yet</Text>
                            )}
                        </>
                    )}
                </View>
            </ScrollView>

            {/* Footer - User Profile */}
            <TouchableOpacity style={styles.footer} onPress={onOpenSettings}>
                <View style={styles.userProfile}>
                    <View style={styles.avatar}>
                        <Text style={styles.avatarText}>G</Text>
                    </View>
                    <View style={styles.userInfo}>
                        <Text style={styles.userName}>Goddexx Snow</Text>
                        <Text style={styles.userPlan}>Pro Plan</Text>
                    </View>
                    <Ionicons name="chevron-forward" size={18} color="#9CA3AF" />
                </View>
            </TouchableOpacity>

            {/* Project Modal */}
            {projectModal.visible && (
                <TouchableOpacity
                    style={styles.modalOverlay}
                    activeOpacity={1}
                    onPress={() => setProjectModal({ ...projectModal, visible: false })}
                >
                    <TouchableOpacity
                        activeOpacity={1}
                        onPress={(e) => e.stopPropagation()}
                        style={styles.modalContent}
                    >
                        <Text style={styles.modalTitle}>
                            {projectModal.mode === 'create' ? 'New Project' : 'Edit Project'}
                        </Text>

                        <Text style={styles.modalLabel}>Name</Text>
                        <TextInput
                            style={styles.modalInput}
                            value={projectModal.name}
                            onChangeText={(t) => setProjectModal({ ...projectModal, name: t })}
                            placeholder="Project Name"
                            placeholderTextColor="#9CA3AF"
                            autoFocus
                        />

                        {/* Color Picker */}
                        <Text style={styles.modalLabel}>Color</Text>
                        <View style={styles.colorPalette}>
                            {colorPalette.map((color) => (
                                <TouchableOpacity
                                    key={color}
                                    style={[
                                        styles.colorSwatch,
                                        { backgroundColor: color },
                                        projectModal.color === color && styles.colorSwatchSelected
                                    ]}
                                    onPress={() => setProjectModal({ ...projectModal, color })}
                                />
                            ))}
                        </View>

                        {/* Icon Picker */}
                        <Text style={styles.modalLabel}>Icon</Text>
                        <View style={styles.iconPalette}>
                            {iconOptions.map((icon) => (
                                <TouchableOpacity
                                    key={icon}
                                    style={[
                                        styles.iconOption,
                                        projectModal.icon === icon && styles.iconOptionSelected
                                    ]}
                                    onPress={() => setProjectModal({ ...projectModal, icon })}
                                >
                                    <Ionicons name={icon as any} size={20} color={projectModal.icon === icon ? '#3D3D3D' : '#9CA3AF'} />
                                </TouchableOpacity>
                            ))}
                        </View>

                        <View style={styles.modalButtons}>
                            <TouchableOpacity onPress={() => setProjectModal({ ...projectModal, visible: false })}>
                                <Text style={styles.cancelButton}>Cancel</Text>
                            </TouchableOpacity>
                            <TouchableOpacity style={styles.saveButton} onPress={saveProject}>
                                <Text style={styles.saveButtonText}>Save</Text>
                            </TouchableOpacity>
                        </View>
                    </TouchableOpacity>
                </TouchableOpacity>
            )}
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: 'transparent',
        position: 'relative',
    },
    topSection: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        paddingHorizontal: 12,
        paddingVertical: 12,
    },
    newChatButton: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 8,
    },
    newChatText: {
        color: '#3D3D3D',
        fontSize: 14,
        fontWeight: '500',
    },
    hamburgerButton: {
        padding: 6,
        marginRight: 8,
    },
    scrollContent: {
        flex: 1,
        paddingHorizontal: 12,
    },
    section: {
        marginTop: 20,
    },
    sectionHeader: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        paddingHorizontal: 8,
        paddingVertical: 6,
        marginBottom: 4,
    },
    sectionTitle: {
        color: '#5E5E5E',
        fontSize: 12,
        fontWeight: '500',
    },
    navItem: {
        flexDirection: 'row',
        alignItems: 'center',
        paddingVertical: 10,
        paddingHorizontal: 8,
        borderRadius: 8,
        gap: 12,
    },
    navItemActive: {
        backgroundColor: 'rgba(255,255,255,0.4)',
    },
    projectRow: {
        flexDirection: 'row',
        alignItems: 'center',
        position: 'relative',
    },
    projectIcon: {
        width: 28,
        height: 28,
        borderRadius: 6,
        backgroundColor: '#E0D7FE',
        alignItems: 'center',
        justifyContent: 'center',
    },
    ellipsisButton: {
        padding: 8,
        marginLeft: 4,
    },
    projectOptionsMenu: {
        position: 'absolute',
        top: '100%',
        right: 0,
        backgroundColor: 'rgba(255,255,255,0.95)',
        borderRadius: 12,
        padding: 8,
        minWidth: 150,
        zIndex: 200,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.15,
        shadowRadius: 12,
        elevation: 8,
    },
    menuItem: {
        flexDirection: 'row',
        alignItems: 'center',
        padding: 10,
        gap: 10,
        borderRadius: 8,
    },
    menuItemText: {
        fontSize: 14,
        color: '#3D3D3D',
    },
    navItemText: {
        color: '#3D3D3D',
        fontSize: 14,
        flex: 1,
    },
    chatItem: {
        paddingVertical: 10,
        paddingHorizontal: 8,
        borderRadius: 8,
    },
    chatItemActive: {
        backgroundColor: 'rgba(255,255,255,0.4)',
    },
    chatItemText: {
        color: '#3D3D3D',
        fontSize: 14,
    },
    emptyText: {
        color: '#9CA3AF',
        fontSize: 14,
        paddingHorizontal: 8,
        fontStyle: 'italic',
    },
    footer: {
        position: 'absolute',
        bottom: 0,
        left: 0,
        right: 0,
        paddingHorizontal: 12,
        paddingVertical: 16,
    },
    userProfile: {
        flexDirection: 'row',
        alignItems: 'center',
    },
    avatar: {
        width: 32,
        height: 32,
        borderRadius: 16,
        backgroundColor: '#E0D7FE',
        alignItems: 'center',
        justifyContent: 'center',
    },
    avatarText: {
        color: '#3D3D3D',
        fontSize: 14,
        fontWeight: '600',
    },
    userInfo: {
        marginLeft: 12,
    },
    userName: {
        color: '#3D3D3D',
        fontSize: 14,
        fontWeight: '500',
    },
    userPlan: {
        color: '#5E5E5E',
        fontSize: 12,
    },
    modalOverlay: {
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0,0,0,0.2)',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 100,
    },
    modalContent: {
        width: '90%',
        maxWidth: 320,
        backgroundColor: 'rgba(255,255,255,0.95)',
        borderRadius: 16,
        padding: 24,
    },
    modalTitle: {
        fontSize: 20,
        fontWeight: '600',
        color: '#3D3D3D',
        marginBottom: 16,
    },
    modalLabel: {
        fontSize: 14,
        fontWeight: '500',
        color: '#5E5E5E',
        marginBottom: 4,
    },
    modalInput: {
        backgroundColor: 'rgba(255,255,255,0.6)',
        borderWidth: 1,
        borderColor: 'rgba(255,255,255,0.4)',
        borderRadius: 12,
        padding: 12,
        marginBottom: 16,
        color: '#3D3D3D',
    },
    modalButtons: {
        flexDirection: 'row',
        justifyContent: 'flex-end',
        gap: 12,
    },
    cancelButton: {
        color: '#5E5E5E',
        fontWeight: '500',
        paddingHorizontal: 16,
        paddingVertical: 8,
    },
    saveButton: {
        backgroundColor: '#E0D7FE',
        paddingHorizontal: 24,
        paddingVertical: 8,
        borderRadius: 12,
    },
    saveButtonText: {
        color: '#3D3D3D',
        fontWeight: '500',
    },
    colorPalette: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        gap: 8,
        marginBottom: 16,
    },
    colorSwatch: {
        width: 32,
        height: 32,
        borderRadius: 8,
        borderWidth: 2,
        borderColor: 'transparent',
    },
    colorSwatchSelected: {
        borderColor: '#3D3D3D',
    },
    iconPalette: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        gap: 8,
        marginBottom: 16,
    },
    iconOption: {
        width: 40,
        height: 40,
        borderRadius: 10,
        backgroundColor: 'rgba(255,255,255,0.4)',
        alignItems: 'center',
        justifyContent: 'center',
        borderWidth: 2,
        borderColor: 'transparent',
    },
    iconOptionSelected: {
        borderColor: '#3D3D3D',
        backgroundColor: 'rgba(224, 215, 254, 0.5)',
    },
});
